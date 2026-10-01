const test = require('node:test')
const assert = require('node:assert/strict')
const {
  createSessionHarness, seedPrivateData, assertPrivateDataCleared, user, axios,
} = require('./helpers/session-harness.cjs')

const anonymous = (hasRefresh) => ({
  authenticated: false, user: null, has_refresh_token: hasRefresh,
})
const authenticated = () => ({
  authenticated: true, user: user('A'), has_refresh_token: true,
})

test('an anonymous visitor without refresh makes no refresh or CSRF request', async () => {
  const h = createSessionHarness()
  const checked = h.auth.checkAuthentication()
  const request = await h.take('check-authentication/')
  request.respond(anonymous(false))

  assert.equal(await checked, false)
  assert.equal(h.auth.user, null)
  assert.equal(h.count('check-authentication/'), 1)
  assert.equal(h.count('refresh-access/'), 0)
  assert.equal(h.count('csrf/'), 0)
})

test('a missing access with valid refresh recovers the profile after page reload', async () => {
  const h = createSessionHarness()
  const checked = h.auth.checkAuthentication()
  const first = await h.take('check-authentication/')
  first.respond(anonymous(true))
  const refresh = await h.take('refresh-access/')
  assert.equal(refresh.config.headers.get('X-CSRFToken'), 'test-csrf')
  assert.equal(refresh.config.withCredentials, true)
  refresh.respond(null)
  const second = await h.take('check-authentication/')
  assert.equal(second.config.signal, first.config.signal)
  second.respond(authenticated())

  assert.equal(await checked, true)
  assert.equal(h.auth.user.email, user('A').email)
  assert.equal(h.record.progressRecord.user.email, user('A').email)
  assert.equal(h.count('check-authentication/'), 2)
  assert.equal(h.count('refresh-access/'), 1)
  assert.equal(h.count('logout/'), 0)
})

test('a refused refresh clears private data without looping or issuing logout', async () => {
  const h = createSessionHarness()
  seedPrivateData(h)
  const checked = h.auth.checkAuthentication()
  const first = await h.take('check-authentication/')
  first.respond(anonymous(true))
  const refresh = await h.take('refresh-access/')
  refresh.respond(null, 401)

  assert.equal(await checked, false)
  assert.equal(h.auth.user, null)
  assertPrivateDataCleared(h)
  assert.equal(h.count('check-authentication/'), 1)
  assert.equal(h.count('refresh-access/'), 1)
  assert.equal(h.count('logout/'), 0)
})

test('remaining anonymous after refresh stops after the second check', async () => {
  const h = createSessionHarness()
  const checked = h.auth.checkAuthentication()
  const first = await h.take('check-authentication/')
  first.respond(anonymous(true))
  const refresh = await h.take('refresh-access/')
  refresh.respond(null)
  const second = await h.take('check-authentication/')
  second.respond(anonymous(true))

  assert.equal(await checked, false)
  assert.equal(h.count('refresh-access/'), 1)
  assert.equal(h.count('check-authentication/'), 2)
})

test('a refresh network failure preserves the current identity and reports the error', async () => {
  const h = createSessionHarness()
  seedPrivateData(h)
  const rejected = assert.rejects(h.auth.checkAuthentication(),
    (error) => error.code === 'ERR_NETWORK')
  const first = await h.take('check-authentication/')
  first.respond(anonymous(true))
  const refresh = await h.take('refresh-access/')
  refresh.fail()
  await rejected

  assert.equal(h.auth.user.email, user('A').email)
  assert.equal(h.records.progressRecords.length, 1)
  assert.equal(h.count('logout/'), 0)
  assert.equal(h.navigation.length, 0)
})

test('a check from A cancelled during refresh cannot clear the new B session', async () => {
  const h = createSessionHarness()
  seedPrivateData(h)
  const rejected = assert.rejects(h.auth.checkAuthentication(), axios.isCancel)
  const first = await h.take('check-authentication/')
  first.respond(anonymous(true))
  const refresh = await h.take('refresh-access/')
  h.auth.setSessionUser(user('B'))
  refresh.respond(null, 401)
  await rejected

  assert.equal(h.auth.user.email, user('B').email)
  assert.equal(h.count('check-authentication/'), 1)
  assert.equal(h.navigation.length, 0)
})

test('concurrent authentication checks share the same pending refresh', async () => {
  const h = createSessionHarness()
  h.auth.setSessionUser(user('A'))
  const checks = [h.auth.checkAuthentication(), h.auth.checkAuthentication()]
  const first = await h.take('check-authentication/')
  const second = await h.take('check-authentication/')
  first.respond(anonymous(true))
  second.respond(anonymous(true))
  const refresh = await h.take('refresh-access/')
  refresh.respond(null)
  const firstRecheck = await h.take('check-authentication/')
  const secondRecheck = await h.take('check-authentication/')
  firstRecheck.respond(authenticated())
  secondRecheck.respond(authenticated())

  assert.deepEqual(await Promise.all(checks), [true, true])
  assert.equal(h.count('refresh-access/'), 1)
  assert.equal(h.count('check-authentication/'), 4)
})
