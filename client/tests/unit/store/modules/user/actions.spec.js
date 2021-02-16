import actions from '@/store/modules/user/actions'
import { Store } from 'vuex-mock-store'
// import { loginUser } from '@/service/teacher_auth'

const { LOGIN_USER } = actions

const mockStore = new Store({
  state: {
    user: {
      current_user: {}
    }
  },
  mutations: {
    'app/TOGGLE_APP_LOADING': 'from app',
    'app/TOGGLE_APP_LOGGED_IN': 'from app',
    'app/TOGGLE_ERROR': 'from app'
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

describe('User actions', () => {
  it('executes LOGIN_USER', () => {
    const payload = {
      email: 'someone@example.com',
      password: 'asdfghj'
    }
    // TODO: Mock auth service calls
    // jest.spyOn(loginUser)
    LOGIN_USER(mockStore, payload)
    expect(mockStore.commit).toHaveBeenCalledTimes(2)
  })
})
