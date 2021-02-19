import Vue from 'vue'
import Vuetify from 'vuetify'
import ConfirmStudentAccount from '@/views/ConfirmStudentAccount'
import { createLocalVue, shallowMount } from '@vue/test-utils'
import { Store } from 'vuex-mock-store'

Vue.use(Vuetify)
const localVue = createLocalVue()

describe('ConfirmStudentAccount.vue', () => {
  let vuetify
  let $store
  const $route = {
    query: {
      token: 'test_token'
    }
  }

  beforeEach(() => {
    vuetify = new Vuetify()
    $store = new Store({
      state: {
        app: {
          loading: 'from app'
        }
      },
      actions: {
        'actions/CONFRIMSTUDENTACCOUNT': 'from user'
      }
    })
  })

  it('renders correctly', () => {
    const wrapper = shallowMount(ConfirmStudentAccount, { localVue, vuetify, mocks: { $store: $store, $route: $route } })
    expect(wrapper).toMatchSnapshot()
  })
})
