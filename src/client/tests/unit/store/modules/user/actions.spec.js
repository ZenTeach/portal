import actions from '@/store/modules/user'
import { Store } from 'vuex-mock-store'
import Vuex from 'vuex'
// eslint-disable-next-line import/no-webpack-loader-syntax
const actionsInjector = require('inject-loader!./actions')
// eslint-disable-next-line no-unused-vars
const _actions = actionsInjector({
  '../api/shop': {
    getProducts (cb) {
      setTimeout(() => {
        // eslint-disable-next-line standard/no-callback-literal
        cb([
          /* mocked response */
        ])
      }, 100)
    }
  }
})
const { LOGIN_USER, SIGNOUT_USER, REGISTER_USER, FETCHCURRENTUSER } = actions

const mockStore = new Store({
  state: {
    user: {
      current_user: {}
    }
  },
  getters: {
    'user/getCurrentUser': 'from user'
  },
  actions: {
    'actions/LOGIN_USER': 'from user',
    'actions/SIGNOUT_USER': 'from user',
    'actions/REGISTER_USER': 'from user',
    'actions/FETCHCURRENTUSER': 'from user'
  }
})

// const mockStore

describe('Vuex user actions', () => {
  beforeEach(() => {})
  // const mockStore = new Vuex()
  it.skip('executes LOGIN_USER', () => {
    const payload = {
      email: 'someone@example.com',
      password: 'asdfghj'
    }

    LOGIN_USER(mockStore, payload)
    expect(mockStore.dispatch).toHaveBeenCalledWith('user/LOGIN_USER')
  })
})
