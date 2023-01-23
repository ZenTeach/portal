import serviceConfig from '@/service/serviceConfig'
import axios from 'axios'
import createAuthRefreshInterceptor from 'axios-auth-refresh'
import store from '../store'
import router from '../router'
import lodash from 'lodash'
// eslint-disable-next-line symbol-description
const singleton = Symbol()
// eslint-disable-next-line symbol-description
const singletonEnforcer = Symbol()
class ApiService {
  constructor (enforcer) {
    if (enforcer !== singletonEnforcer) {
      throw new Error('Cannot construct singleton')
    }

    this.session = axios.create(serviceConfig)

    const silentRefreshLogic = failedRequest => {
      return new Promise((resolve, reject) => {
        if (failedRequest.status === 400 || failedRequest.status === 404) {
          const { message } = failedRequest.response.data
          store.dispatch('app/TOGGLE_ERROR', message, { root: true })
          store.dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
          store.dispatch('user/SIGNOUT_USER', {}, { root: true })
          router.push({ name: 'login' })
          resolve()
        } else {
          this.post('/teacher/token/refresh')
            .then(response => {
              if (response.status === 200) {
                resolve(response)
              }
            })
            .catch(error => {
              store.dispatch('app/TOGGLE_ERROR', error.response.data, {
                root: true
              })
              store.dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
              store.dispatch('user/SIGNOUT_USER', {}, { root: true })
              store.commit('app/TOGGLE_APP_LOADING', false, { root: true })
              router.push({ name: 'login' })
              reject(error)
            })
        }
      })
    }
    createAuthRefreshInterceptor(this.session, silentRefreshLogic, {
      statusCodes: [401]
    })
  }

  static get instance () {
    if (!this[singleton]) {
      const instance = new ApiService(singletonEnforcer)
      this[singleton] = new Proxy(instance, {
        get: (obj, prop) => {
          return obj[prop]
        }
      })
    }

    return this[singleton]
  }

  // build custom header for axios request
  buildHeader (header) {
    // use lodash to merge header and return a new object
    const mergedHeader = lodash.merge(...header)
    return { headers: mergedHeader }
  }

  fetchCookieByName (name) {
    if (document.cookie.length === 0) {
      return ''
    }
    var csrfCookie = document.cookie.split('; ').find(row => row.startsWith(name))

    if (csrfCookie !== undefined) {
      return csrfCookie.split('=')[1]
    } else {
      return ''
    }
  }

  csrfDoubleSubmitHeader () {
    const accessCsrfCookieValue = this.fetchCookieByName('csrf_access_token')
    const refreshCsrfCookieValue = this.fetchCookieByName('csrf_refresh_token')
    return {
      'X-CSRF-ACCESS-TOKEN': accessCsrfCookieValue,
      'X-CSRF-REFRESH-TOKEN': refreshCsrfCookieValue
    }
  }

  pushToHeader (main, dict) {
    return { ...main, ...dict }
  }

  async get (...params) {
    const updatedHeaders = this.buildHeader(params.headers, this.csrfDoubleSubmitHeader())
    return Promise.resolve(this.session.get(...params, updatedHeaders))
  }

  async post (...params) {
    const updatedHeaders = this.buildHeader(params.headers, this.csrfDoubleSubmitHeader())

    return Promise.resolve(this.session.post(...params, updatedHeaders))
  }

  async put (...params) {
    const updatedHeaders = this.buildHeader(params.headers, this.csrfDoubleSubmitHeader())

    return Promise.resolve(this.session.put(...params, updatedHeaders))
  }

  async patch (...params) {
    const updatedHeaders = this.buildHeader(params.headers, this.csrfDoubleSubmitHeader())

    return Promise.resolve(this.session.patch(...params, updatedHeaders))
  }

  async remove (...params) {
    const updatedHeaders = this.buildHeader(params.headers, this.csrfDoubleSubmitHeader())

    return Promise.resolve(this.session.delete(...params, updatedHeaders))
  }
}
export default ApiService.instance
