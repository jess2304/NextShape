const test = require('node:test')
const assert = require('node:assert/strict')
const {
  createSessionHarness, seedPrivateData, assertPrivateDataCleared, user, axios,
} = require('./helpers/session-harness.cjs')

test('logging in as B clears all private A data and discards a late history response', async () => {
  const h = createSessionHarness()
  seedPrivateData(h)
  const oldHistory = h.records.getProgressRecords()
  const oldRejected = assert.rejects(oldHistory, axios.isCancel)
  const pending = await h.take('progress-records/')

  const login = h.auth.login({ email: user('B').email, password: 'test-password' })
  const request = await h.take('login/')
  assertPrivateDataCleared(h)
  request.respond(user('B'))
  await login
  pending.respond([{ id: 1, weight_kg: 78 }])
  await oldRejected

  assert.equal(h.auth.user.email, user('B').email)
  assert.equal(h.record.progressRecord.user.email, user('B').email)
  assertPrivateDataCleared(h)
  assert.equal(h.count('logout/'), 0)
})

test('a late A failure cannot refresh or log B out', async () => {
  const h = createSessionHarness()
  seedPrivateData(h)
  const rejected = assert.rejects(h.records.getProgressRecords(), axios.isCancel)
  const pending = await h.take('progress-records/')
  h.auth.setSessionUser(user('B'))
  pending.respond(null, 401)
  await rejected
  assert.equal(h.auth.user.email, user('B').email)
  assert.equal(h.count('refresh-access/'), 0)
  assert.equal(h.navigation.length, 0)
})

test('a session switch between promise resolution and commit skips both apply and finish', async () => {
  const h = createSessionHarness()
  h.auth.setSessionUser(user('A'))
  let applied = false
  let finished = false
  const request = h.api.runSessionRequest(
    () => Promise.resolve('A'),
    () => { applied = true },
    () => { finished = true },
  )
  h.auth.setSessionUser(user('B'))
  await assert.rejects(request, axios.isCancel)
  assert.equal(applied, false)
  assert.equal(finished, false)
})

test('an old coach finally cannot stop the loading indicator of B', async () => {
  const h = createSessionHarness()
  h.auth.setSessionUser(user('A'))
  const oldRejected = assert.rejects(h.coach.buildWeekPlan(), axios.isCancel)
  const oldPlan = await h.take('coach/week-plan/', 'post')
  h.auth.setSessionUser(user('B'))
  const build = h.coach.buildWeekPlan()
  const newPlan = await h.take('coach/week-plan/', 'post')

  oldPlan.respond({ plan: { owner: 'A' }, updated_at: 'old' })
  await oldRejected
  assert.equal(h.coach.isPlanLoading, true)
  assert.equal(h.coach.weekPlan, null)

  newPlan.respond({ plan: { owner: 'B' }, updated_at: 'new' })
  await build
  assert.equal(h.coach.weekPlan.owner, 'B')
  assert.equal(h.coach.weekPlanUpdatedAt, 'new')
  assert.equal(h.coach.isPlanLoading, false)
})

test('a late profile update cannot replace the current user', async () => {
  const h = createSessionHarness()
  h.auth.setSessionUser(user('A'))
  const rejected = assert.rejects(h.auth.updateProfileField('first_name', 'Alice'), axios.isCancel)
  const pending = await h.take('profile/')
  h.auth.setSessionUser(user('B'))
  pending.respond({ ...user('A'), first_name: 'Alice' })
  await rejected
  assert.equal(h.auth.user.email, user('B').email)
})

test('late calorie results cannot repopulate the next account calculator', async () => {
  const h = createSessionHarness()
  seedPrivateData(h)
  const rejected = assert.rejects(h.record.calculateCalories(), axios.isCancel)
  const pending = await h.take('calculate-calories/')
  h.auth.setSessionUser(user('B'))
  pending.respond({ bmr: 1700, tdee: 2100, calories_recommandees: 1900 })
  await rejected
  assertPrivateDataCleared(h)
})

test('profile is hydrated from the server after reload without persisted auth data', async () => {
  const h = createSessionHarness()
  assert.equal(h.auth.user, null)
  const checked = h.auth.checkAuthentication()
  const pending = await h.take('check-authentication/')
  pending.respond({ authenticated: true, user: user('B') })
  assert.equal(await checked, true)
  assert.equal(h.auth.user.email, user('B').email)
  assert.equal(h.record.progressRecord.user.email, user('B').email)
})

test('an authentication network failure propagates without declaring the user logged out', async () => {
  const h = createSessionHarness()
  seedPrivateData(h)
  const rejected = assert.rejects(h.auth.checkAuthentication(), (error) => error.code === 'ERR_NETWORK')
  const pending = await h.take('check-authentication/')
  pending.fail()
  await rejected
  assert.equal(h.auth.user.email, user('A').email)
  assert.equal(h.records.progressRecords.length, 1)
  assert.equal(h.count('logout/'), 0)
})

test('server confirmation of an anonymous session clears every private store', async () => {
  const h = createSessionHarness()
  seedPrivateData(h)
  const checked = h.auth.checkAuthentication()
  const pending = await h.take('check-authentication/')
  pending.respond({ authenticated: false, user: null })
  assert.equal(await checked, false)
  assert.equal(h.auth.user, null)
  assertPrivateDataCleared(h)
  assert.equal(h.count('logout/'), 0)
})

test('concurrent 401 responses share one refresh and replay their requests', async () => {
  const h = createSessionHarness()
  h.auth.setSessionUser(user('A'))
  const history = h.records.getProgressRecords()
  const preferences = h.coach.loadNutritionPreferences()
  const historyRequest = await h.take('progress-records/')
  const preferencesRequest = await h.take('nutrition-preferences/')
  historyRequest.respond(null, 401)
  preferencesRequest.respond(null, 401)
  const refresh = await h.take('refresh-access/')
  assert.equal(refresh.config.headers.get('X-CSRFToken'), 'test-csrf')
  refresh.respond(null)
  const replayHistory = await h.take('progress-records/')
  const replayPreferences = await h.take('nutrition-preferences/')
  replayHistory.respond([{ id: 2, weight_kg: 80 }])
  replayPreferences.respond({ allergies: 'Berries' })
  await Promise.all([history, preferences])
  assert.equal(h.count('refresh-access/'), 1)
  assert.equal(h.records.progressRecords[0].id, 2)
  assert.equal(h.coach.nutritionPreferences.allergies, 'Berries')
})

test('a repeated 401 expires local data after one retry instead of looping', async () => {
  const h = createSessionHarness()
  seedPrivateData(h)
  const rejected = assert.rejects(h.records.getProgressRecords(), axios.isCancel)
  const pending = await h.take('progress-records/')
  pending.respond(null, 401)
  const refresh = await h.take('refresh-access/')
  refresh.respond(null)
  const replay = await h.take('progress-records/')
  replay.respond(null, 401)
  await rejected
  assert.equal(h.count('refresh-access/'), 1)
  assert.equal(h.auth.user, null)
  assertPrivateDataCleared(h)
})

test('a refresh failure from A cannot expire a new B session', async () => {
  const h = createSessionHarness()
  h.auth.setSessionUser(user('A'))
  const rejected = assert.rejects(h.records.getProgressRecords(), axios.isCancel)
  const pending = await h.take('progress-records/')
  pending.respond(null, 401)
  const refresh = await h.take('refresh-access/')
  h.auth.setSessionUser(user('B'))
  refresh.respond(null, 401)
  await rejected
  assert.equal(h.auth.user.email, user('B').email)
  assert.equal(h.navigation.length, 0)
})

test('ordinary 403 errors remain rejected without refresh or logout', async () => {
  const h = createSessionHarness()
  h.auth.setSessionUser(user('A'))
  const rejected = assert.rejects(h.auth.updateProfileField('first_name', 'Alice'),
    (error) => error.response?.status === 403)
  const pending = await h.take('profile/')
  assert.equal(pending.config.headers.get('X-CSRFToken'), 'test-csrf')
  pending.respond(null, 403)
  await rejected
  assert.equal(h.auth.user.email, user('A').email)
  assert.equal(h.count('refresh-access/'), 0)
})

test('a CSRF fetch failure during refresh is not treated as a rejected refresh token', async () => {
  const h = createSessionHarness({ autoCsrf: false })
  h.auth.setSessionUser(user('A'))
  const rejected = assert.rejects(h.records.getProgressRecords(), (error) => error.response?.status === 401)
  const pending = await h.take('progress-records/')
  pending.respond(null, 401)
  const csrf = await h.take('csrf/')
  csrf.respond(null, 401)
  await rejected
  assert.equal(h.auth.user.email, user('A').email)
  assert.equal(h.count('refresh-access/'), 0)
  assert.equal(h.navigation.length, 0)
})

test('account deletion clears state without issuing logout for an already deleted user', async () => {
  const h = createSessionHarness()
  seedPrivateData(h)
  const deleted = h.auth.deleteAccount()
  const request = await h.take('delete-account/', 'delete')
  request.respond(null)
  await deleted
  assert.equal(h.auth.user, null)
  assertPrivateDataCleared(h)
  assert.equal(h.count('logout/'), 0)
  assert.equal(h.auth.isChangingSession, false)
})

test('failed logout is reported, then a successful retry clears the session', async () => {
  const h = createSessionHarness()
  seedPrivateData(h)
  const rejected = assert.rejects(h.auth.logout(), (error) => error.code === 'ERR_NETWORK')
  const failure = await h.take('logout/')
  failure.fail()
  await rejected
  assert.equal(h.auth.user.email, user('A').email)
  assert.equal(h.auth.isChangingSession, false)
  assert.equal(h.navigation.length, 0)

  const logout = h.auth.logout()
  const success = await h.take('logout/')
  success.respond(null)
  await logout
  assert.equal(h.auth.user, null)
  assertPrivateDataCleared(h)
})

test('a pending logout prevents a competing login from changing shared cookies', async () => {
  const h = createSessionHarness()
  h.auth.setSessionUser(user('A'))
  const logout = h.auth.logout()
  const pending = await h.take('logout/')
  await assert.rejects(h.auth.login({ email: user('B').email, password: 'test-password' }), axios.isCancel)
  assert.equal(h.count('login/'), 0)
  pending.respond(null)
  await logout
  assert.equal(h.auth.user, null)
  assert.equal(h.auth.isChangingSession, false)
})

test('a change in another tab clears data and forces a fresh navigation without broadcasting private data', async () => {
  const h = createSessionHarness()
  const stop = h.startSessionSync()
  const channel = h.channels[0]
  seedPrivateData(h)
  const rejected = assert.rejects(h.records.getProgressRecords(), axios.isCancel)
  const pending = await h.take('progress-records/')

  channel.receive('changed')
  pending.respond([{ id: 1, weight_kg: 78 }])
  await rejected
  assert.equal(h.auth.user, null)
  assertPrivateDataCleared(h)
  assert.equal(h.navigation[0].path, '/')
  assert.equal(h.navigation[0].force, true)
  assert.equal(channel.messages.length, 0)

  h.auth.setSessionUser(user('B'), true)
  assert.deepEqual(channel.messages, ['changed'])
  stop()
})

test('history edits find the record by ID after an intervening reordering', async () => {
  const h = createSessionHarness()
  h.auth.setSessionUser(user('A'))
  h.records.progressRecords = [{ id: 1, weight_kg: 78 }, { id: 2, weight_kg: 82 }]
  const update = h.records.updateRecord(1, { weight_kg: 79 })
  const pending = await h.take('progress-records/1/', 'patch')
  h.records.progressRecords.reverse()
  pending.respond({ id: 1, weight_kg: 79 })
  await update
  assert.equal(h.records.progressRecords[0].id, 2)
  assert.equal(h.records.progressRecords[0].weight_kg, 82)
  assert.equal(h.records.progressRecords[1].id, 1)
  assert.equal(h.records.progressRecords[1].weight_kg, 79)
})

test('history deletion removes only the requested ID after an intervening reordering', async () => {
  const h = createSessionHarness()
  h.auth.setSessionUser(user('A'))
  h.records.progressRecords = [{ id: 1, weight_kg: 78 }, { id: 2, weight_kg: 82 }]
  const deletion = h.records.deleteRecord(1)
  const pending = await h.take('progress-records/1/', 'delete')
  h.records.progressRecords.reverse()
  pending.respond(null)
  await deletion
  assert.equal(h.records.progressRecords.length, 1)
  assert.equal(h.records.progressRecords[0].id, 2)
})

test('account deletion can refresh an expired access token while a session change is in progress', async () => {
  const h = createSessionHarness()
  seedPrivateData(h)
  const deletion = h.auth.deleteAccount()
  const pending = await h.take('delete-account/', 'delete')
  assert.equal(h.auth.isChangingSession, true)
  pending.respond(null, 401)
  const refresh = await h.take('refresh-access/')
  refresh.respond(null)
  const replay = await h.take('delete-account/', 'delete')
  replay.respond(null)
  await deletion
  assert.equal(h.count('refresh-access/'), 1)
  assert.equal(h.auth.user, null)
  assert.equal(h.auth.isChangingSession, false)
  assertPrivateDataCleared(h)
})

test('a refused refresh during deletion clears local data and requests the login page', async () => {
  const h = createSessionHarness()
  seedPrivateData(h)
  const rejected = assert.rejects(h.auth.deleteAccount(), axios.isCancel)
  const pending = await h.take('delete-account/', 'delete')
  pending.respond(null, 401)
  const refresh = await h.take('refresh-access/')
  refresh.respond(null, 401)
  await rejected
  assert.equal(h.auth.user, null)
  assert.equal(h.auth.isChangingSession, false)
  assertPrivateDataCleared(h)
  assert.equal(h.navigation[0], '/connexion')
})
