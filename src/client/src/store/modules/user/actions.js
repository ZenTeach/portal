import {
  loginUser,
  logoutUser,
  registerUser,
  getCurrentUser,
  sendAccountRecovery,
  changePassword
} from '../../../service/user_auth'
import router from '@/router'
import Vue from 'vue'

const LOGIN_USER = ({ commit }, payload) => {
  commit('app/TOGGLE_APP_LOADING', true, { root: true })

  loginUser(payload).then(
    data => {
      commit('app/TOGGLE_APP_LOGGED_IN', true, { root: true })
      router.push('/')
    },
    error => {
      commit('app/TOGGLE_ERROR', error.response.data, { root: true })
    }
  )
  commit('app/TOGGLE_APP_LOADING', false, { root: true })
}

const SIGNOUT_USER = ({ commit }) => {
  commit('app/TOGGLE_APP_LOADING', true, { root: true })
  logoutUser()
  Vue.prototype.$cookies.remove('access_token_cookie')
  commit('app/TOGGLE_APP_LOGGED_IN', false, { root: true })
  commit('TOGGLECURRENTUSER', {})
  commit('app/TOGGLE_APP_LOADING', false, { root: true })
}

const REGISTER_USER = ({ commit }, payload) => {
  commit('app/TOGGLE_APP_LOADING', true, { root: true })
  registerUser(payload)
  commit('app/TOGGLE_APP_LOGGED_IN', true, { root: true })
  commit('app/TOGGLE_APP_LOADING', false, { root: true })
}

const FETCHCURRENTUSER = ({ commit }) => {
  commit('app/TOGGLE_APP_LOADING', true, { root: true })

  getCurrentUser().then(result => {
    const { user } = result
    commit('TOGGLECURRENTUSER', user)
  })
  commit('app/TOGGLE_APP_LOADING', false, { root: true })
}

const SENDACCOUNTRECOVERY = ({ commit }, email) => {
  commit('app/TOGGLE_APP_LOADING', true, { root: true })
  sendAccountRecovery(email).then(result => {
    // TODO: store message
    commit('app/TOGGLE_APP_LOADING', false, { root: true })
    router.push('/')
  })
}

const UPDATEUSERPASSWORD = ({ commit }, payload) => {
  commit('app/TOGGLE_APP_LOADING', true, { root: true })
  changePassword(payload)
    .then(
      data => {
        commit('app/TOGGLE_APP_LOADING', false, { root: true })
        router.push('/')
      },
      error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
        commit('app/TOGGLE_APP_LOADING', false, { root: true })
        router.push('/login')
      }
    )
}

export default {
  LOGIN_USER,
  SIGNOUT_USER,
  REGISTER_USER,
  FETCHCURRENTUSER,
  SENDACCOUNTRECOVERY,
  UPDATEUSERPASSWORD
}
