import {
  loginUser,
  logoutUser,
  registerUser,
  getCurrentUser,
  sendAccountRecovery,
  changePassword,
  confirmAccount,
  userInvite,
  sendConfirmationInstruction
} from '../../../service/teacher_auth'

import { confirmStudentAccount } from '../../../service/student_auth'
import router from '@/router'
import Vue from 'vue'

const LOGIN_USER = ({ commit, dispatch }, payload) => {
  commit('app/TOGGLE_APP_LOADING', true, { root: true })

  loginUser(payload).then(
    data => {
      commit('app/TOGGLE_APP_LOGGED_IN', true, { root: true })
      dispatch('FETCHCURRENTUSER')
      router.push('/')
    },
    error => {
      commit('app/TOGGLE_ERROR', error.response.data, { root: true })
      dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
    }
  )
  commit('app/TOGGLE_APP_LOADING', false, { root: true })
}

const SIGNOUT_USER = ({ commit, dispatch }) => {
  commit('app/TOGGLE_APP_LOADING', true, { root: true })
  logoutUser().then(data => {
    Vue.prototype.$cookies.remove('csrf_access_token')
    commit('app/TOGGLE_APP_LOGGED_IN', false, { root: true })
    commit('TOGGLECURRENTUSER', {})
    commit('app/TOGGLE_APP_LOADING', false, { root: true })
  },
  error => {
    commit('app/TOGGLE_ERROR', error.response.data, { root: true })
    dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
  }
  )
}

const REGISTER_USER = ({ commit, dispatch }, payload) => {
  commit('app/TOGGLE_APP_LOADING', true, { root: true })
  registerUser(payload).then(
    data => {
      commit('app/TOGGLE_APP_LOGGED_IN', true, { root: true })
      commit('app/TOGGLE_APP_LOADING', false, { root: true })
      router.push('/')
    },
    error => {
      commit('app/TOGGLE_APP_LOADING', false, { root: true })
      commit('app/TOGGLE_ERROR', error.response.data, { root: true })
      dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
    }
  )
}

const FETCHCURRENTUSER = ({ commit, dispatch }) => {
  commit('app/TOGGLE_APP_LOADING', true, { root: true })

  getCurrentUser().then(result => {
    const { user } = result
    commit('TOGGLECURRENTUSER', user)
    commit('app/TOGGLE_APP_LOADING', false, { root: true })
  },
  error => {
    commit('app/TOGGLE_APP_LOADING', false, { root: true })
    commit('app/TOGGLE_ERROR', error.response.data, { root: true })
    dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
  })
}

const SENDACCOUNTRECOVERY = ({ commit, dispatch }, email) => {
  commit('app/TOGGLE_APP_LOADING', true, { root: true })
  sendAccountRecovery(email).then(result => {
    commit('app/TOGGLE_APP_LOADING', false, { root: true })
    dispatch('app/TOGGLE_ERROR', result, { root: true })
    dispatch('app/TOGGLE_APP_STATUS', 'success', { root: true })
    router.push('/')
  },
  error => {
    commit('app/TOGGLE_APP_LOADING', false, { root: true })
    commit('app/TOGGLE_ERROR', error.response.data, { root: true })
    dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
  })
}

const UPDATEUSERPASSWORD = ({ commit, dispatch }, payload) => {
  commit('app/TOGGLE_APP_LOADING', true, { root: true })
  changePassword(payload)
    .then(
      data => {
        commit('app/TOGGLE_APP_LOADING', false, { root: true })
        dispatch('app/TOGGLE_ERROR', data, { root: true })
        dispatch('app/TOGGLE_APP_STATUS', 'success', { root: true })
        router.push('/login')
      },
      error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
        commit('app/TOGGLE_APP_LOADING', false, { root: true })
        dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
        router.push('/login')
      }
    )
}

const CONFIRMNEWACCOUNT = ({ commit, dispatch }, token) => {
  commit('app/TOGGLE_APP_LOADING', true, { root: true })
  confirmAccount(token).then(
    _data => {
      commit('app/TOGGLE_APP_LOADING', false, { root: true })
    },
    error => {
      commit('app/TOGGLE_ERROR', error.response.data, { root: true })
      commit('app/TOGGLE_APP_LOADING', false, { root: true })
      dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
    }
  )
}

const CONFRIMSTUDENTACCOUNT = ({ commit, dispatch }, token) => {
  commit('app/TOGGLE_APP_LOADING', true, { root: true })
  confirmStudentAccount(token).then(
    _data => {
      commit('app/TOGGLE_APP_LOADING', false, { root: true })
    },
    error => {
      commit('app/TOGGLE_ERROR', error.response.data, { root: true })
      commit('app/TOGGLE_APP_LOADING', false, { root: true })
      dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
    }
  )
}

const SENDUSERINVITE = ({ commit, dispatch }, email) => {
  userInvite(email).then(
    _data => {
      commit('app/TOGGLE_APP_INVITE_MODAL', false, { root: true })
    },
    error => {
      commit('app/TOGGLE_ERROR', error.response.data, { root: true })
      commit('app/TOGGLE_APP_INVITE_MODAL', false, { root: true })
      dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
    }
  )
}

const SENDUSERCONFIRMATION = ({ commit, dispatch }, email) => {
  sendConfirmationInstruction(email).then(
    data => {
      dispatch('app/TOGGLE_ERROR', data, { root: true })
      dispatch('app/TOGGLE_APP_STATUS', 'success', { root: true })
    },
    error => {
      commit('app/TOGGLE_ERROR', error.response.data, { root: true })
      dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
    }
  )
}

export default {
  LOGIN_USER,
  SIGNOUT_USER,
  REGISTER_USER,
  FETCHCURRENTUSER,
  SENDACCOUNTRECOVERY,
  UPDATEUSERPASSWORD,
  CONFIRMNEWACCOUNT,
  CONFRIMSTUDENTACCOUNT,
  SENDUSERINVITE,
  SENDUSERCONFIRMATION
}
