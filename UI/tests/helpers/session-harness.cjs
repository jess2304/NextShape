const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const vm = require('node:vm')
const ts = require('typescript')
const axios = require('axios')
const { createPinia, setActivePinia } = require('pinia')

const sourceRoot = path.resolve(__dirname, '../../src')

// Load the real application modules without a browser or a new test dependency.
// Only HTTP, navigation and cross-tab messaging are replaced. Pinia, Axios,
// interceptors, stores and their imports all run their production code.
function createSessionHarness({ autoCsrf = true } = {}) {
  const requests = []
  const navigation = []
  const channels = []
  const router = {
    push: async (target) => { navigation.push(target) },
    replace: async (target) => { navigation.push(target) },
  }
  class BroadcastChannel {
    constructor(name) {
      this.name = name
      this.messages = []
      this.listeners = []
      channels.push(this)
    }
    postMessage(message) { this.messages.push(message) }
    addEventListener(event, listener) {
      if (event === 'message') this.listeners.push(listener)
    }
    receive(data) {
      this.onmessage?.({ data })
      for (const listener of this.listeners) listener({ data })
    }
    close() {}
  }

  const adapter = (config) => new Promise((resolve, reject) => {
    const url = new URL(config.url, config.baseURL || 'https://test.invalid/api/')
      .pathname.replace(/^\/api\//, '')
    const request = {
      url,
      config,
      taken: false,
      respond(data, status = 200) {
        const response = {
          config, status, statusText: String(status), headers: {},
          data: { success: status < 400, code: 'TEST', message: '', data },
        }
        if (status < 400) resolve(response)
        else reject(new axios.AxiosError('HTTP error', 'ERR_BAD_REQUEST', config, null, response))
      },
      fail() { reject(new axios.AxiosError('Offline', 'ERR_NETWORK', config)) },
    }
    requests.push(request)
    if (url === 'csrf/' && autoCsrf) request.respond({ csrfToken: 'test-csrf' })
    // Deliberately allow a late response after abort: the application must also
    // protect its state when cancellation arrives after transport completion.
  })
  const testAxios = axios.create({ adapter })
  Object.assign(testAxios, {
    AxiosError: axios.AxiosError,
    CanceledError: axios.CanceledError,
    isAxiosError: axios.isAxiosError,
    isCancel: axios.isCancel,
    create: (config) => axios.create({ ...config, adapter }),
  })
  const context = vm.createContext({
    console, AbortController, URL, Date, Promise, setTimeout, clearTimeout,
    BroadcastChannel, window: { BroadcastChannel },
  })
  const modules = new Map()
  function load(filename) {
    filename = path.resolve(filename)
    if (modules.has(filename)) return modules.get(filename).exports
    const module = { exports: {} }
    modules.set(filename, module)
    const source = fs.readFileSync(filename, 'utf8').replaceAll('import.meta.env',
      '({ VITE_API_URL: "https://test.invalid/api/", BASE_URL: "/" })')
    const { outputText } = ts.transpileModule(source, {
      fileName: filename,
      compilerOptions: {
        target: ts.ScriptTarget.ES2022,
        module: ts.ModuleKind.CommonJS,
        esModuleInterop: true,
      },
    })
    const localRequire = (specifier) => {
      if (specifier === 'axios') return testAxios
      if (specifier === '@/router') return { __esModule: true, default: router }
      if (specifier.startsWith('@/')) return load(path.join(sourceRoot, `${specifier.slice(2)}.ts`))
      if (specifier.startsWith('.')) return load(path.resolve(path.dirname(filename), `${specifier}.ts`))
      return require(specifier)
    }
    const evaluate = vm.runInContext(`(function(require, module, exports) {\n${outputText}\n})`, context, { filename })
    evaluate(localRequire, module, module.exports)
    return module.exports
  }

  setActivePinia(createPinia())
  const api = load(path.join(sourceRoot, 'services/apiService.ts'))
  const authModule = load(path.join(sourceRoot, 'stores/authStore.ts'))
  const auth = authModule.useAuthStore()
  const records = load(path.join(sourceRoot, 'stores/progressRecordsStore.ts')).useProgressRecords()
  const record = load(path.join(sourceRoot, 'stores/progressRecordStore.ts')).useProgressRecord()
  const coach = load(path.join(sourceRoot, 'stores/coachStore.ts')).useCoachStore()

  return {
    api, auth, records, record, coach, requests, navigation, channels,
    startSessionSync: authModule.startSessionSync,
    async take(url, method) {
      for (let attempt = 0; attempt < 100; attempt++) {
        const request = requests.find((candidate) => !candidate.taken && candidate.url === url
          && (!method || candidate.config.method === method))
        if (request) {
          request.taken = true
          return request
        }
        await new Promise(setImmediate)
      }
      assert.fail(`Expected ${method || '*'} ${url}; observed ${requests.map((r) => `${r.config.method} ${r.url}`).join(', ')}`)
    },
    count(url) { return requests.filter((request) => request.url === url).length },
  }
}

const user = (name) => ({
  first_name: name, last_name: 'Test', email: `${name}@example.test`,
  gender: 'M', birth_date: '1990-01-01', phone_number: '',
})

function seedPrivateData(harness, owner = user('A')) {
  harness.auth.setSessionUser(owner)
  harness.records.progressRecords = [{ id: 1, weight_kg: 78 }]
  harness.record.progressRecord.weight_kg = 78
  harness.record.progressRecord.bmr = 1700
  harness.coach.nutritionPreferences.allergies = 'private allergy'
  harness.coach.weekPlan = { days: [{ private: 'menu A' }] }
  harness.coach.weekPlanUpdatedAt = '2026-01-01'
}

function assertPrivateDataCleared(harness) {
  assert.equal(harness.records.progressRecords.length, 0)
  assert.equal(harness.record.progressRecord.weight_kg, null)
  assert.equal(harness.record.progressRecord.bmr, null)
  assert.equal(harness.coach.nutritionPreferences.allergies, '')
  assert.equal(harness.coach.weekPlan, null)
  assert.equal(harness.coach.weekPlanUpdatedAt, null)
  assert.equal(harness.coach.isPlanLoading, false)
}

module.exports = { createSessionHarness, seedPrivateData, assertPrivateDataCleared, user, axios }
