import { shallowMount, createLocalVue } from '@vue/test-utils'
import AccountConfirmation from '@/views/AccountConfirmation.vue'
import Vuex from 'vuex'
import Vue from 'vue'
import Vuetify from 'vuetify'
import { Store } from 'vuex-mock-store'

Vue.use(Vuetify)
const localVue = createLocalVue()
localVue.use(Vuex)

describe('AccountConfirmation.vue', () => {
  let vuetify
  let store
  const $route = {
    query: {
      token: 'test_token'
    }
  }

  beforeEach(() => {
    store = new Store({
      state: {
        app: { loading: false }
      },
      getters: {
        getter: () => 'from A'
      }

    })
    // store = new Vuex.Store({
    //   modules: {
    //     app: {
    //       state: {
    //         loading: false
    //       }
    //     }
    //   }
    // })
    vuetify = new Vuetify()
  })
  it('has renders the view correctly', () => {
    const wrapper = shallowMount(AccountConfirmation, { store, localVue, vuetify, mocks: { $route } })
    expect(wrapper).toMatchSnapshot()
  })
})
