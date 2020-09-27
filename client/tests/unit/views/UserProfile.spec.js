import { shallowMount, createLocalVue } from '@vue/test-utils'
import UserProfile from '@/views/UserProfile.vue'
import VueRouter from 'vue-router'
import Vuex from 'vuex'
import Vue from 'vue'
import { Store } from 'vuex-mock-store'

import Vuetify from 'vuetify'
Vue.use(Vuetify)

const localVue = createLocalVue()
localVue.use(Vuex)
localVue.use(VueRouter)
const router = new VueRouter()

describe('UserProfile.vue', () => {
  let store
  let vuetify

  beforeEach(() => {
    vuetify = new Vuetify()
    store = new Store({
      state: {
        user: { current_user: {} }
      },
      getters: {
        'user/getCurrentUser': 'from user'
      }

    })
  })
  it('has renders the view correctly', () => {
    const user = {
      firstname: 'john',
      lastname: 'doe'
    }
    store.getters.getCurrentUser = user
    const wrapper = shallowMount(UserProfile, {
      store,
      localVue,
      vuetify,
      router,
      mocks: {
        user
      }
    })
    expect(wrapper).toMatchSnapshot()
  })
})
