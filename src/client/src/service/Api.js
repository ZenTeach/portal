import serviceConfig from '@/service/serviceConfig'
import axios from 'axios'
import createAuthRefreshInterceptor from 'axios-auth-refresh'
import store from '../store'
import router from '../router'
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
      console.log('In Auth-Refresher')
      console.log('Encountered an error', failedRequest.config.url)
      console.log(failedRequest.config.url)
      return new Promise((resolve, reject) => {
        if (failedRequest.status === 400 || failedRequest.status === 404) {
          const { message } = failedRequest.response.data
          store.dispatch('app/TOGGLE_ERROR', message, { root: true })
          store.dispatch('user/SIGNOUT_USER', {}, { root: true })
          router.push({ name: 'login' })
          resolve()
        } else {
          console.log('Refreshing...')
          this.post('/teacher/token/refresh')
            .then(response => {
              if (response.status === 200) {
                console.log('Session Refreshed!')
                resolve(response)
              }
            })
            .catch(error => {
              store.dispatch('app/TOGGLE_ERROR', error.response.data, {
                root: true
              })
              store.dispatch('user/SIGNOUT_USER', {}, { root: true })
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

  csrfDoubleSubmitHeader (cookieName) {
    const csrfCookieValue = this.fetchCookieByName(cookieName)
    return {
      'X-CSRF-TOKEN': csrfCookieValue
    }
  }

  pushToHeader (main, dict) {
    return { ...main, ...dict }
  }

  async get (...params) {
    return Promise.resolve(this.session.get(...params))
  }

  async post (...params) {
    const updatedHeaders = this.pushToHeader({}, this.csrfDoubleSubmitHeader('csrf_access_token'))

    return Promise.resolve(this.session.post(...params, { headers: updatedHeaders }))
  }

  async put (...params) {
    const updatedHeaders = this.pushToHeader(params.headers || {}, this.csrfDoubleSubmitHeader('csrf_access_token'))

    return Promise.resolve(this.session.put(...params, { headers: updatedHeaders }))
  }

  async patch (...params) {
    const updatedHeaders = this.pushToHeader(params.headers || {}, this.csrfDoubleSubmitHeader('csrf_access_token'))

    return Promise.resolve(this.session.patch(...params, { headers: updatedHeaders }))
  }

  async remove (...params) {
    const updatedHeaders = this.pushToHeader(params.headers || {}, this.csrfDoubleSubmitHeader('csrf_access_token'))

    return Promise.resolve(this.session.delete(...params, { headers: updatedHeaders }))
  }
}
export default ApiService.instance
