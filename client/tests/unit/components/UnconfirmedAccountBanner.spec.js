import Vue from 'vue'
import { createLocalVue, shallowMount } from '@vue/test-utils'
import UnconfirmedAccountBanner from '@/components/UnconfirmedAccountBanner'
import Vuetify from 'vuetify'
import { Store } from 'vuex-mock-store'
import Vuex from 'vuex'

Vue.use(Vuetify)
const localVue = createLocalVue()
localVue.use(Vuex)

describe('UnconfirmedAccountBanner.vue', () => {
  let vuetify
  let store
  beforeEach(() => {
    vuetify = new Vuetify()
    store = new Store({
      state: {
        user: {
          current_user: 'from user'
        }
      },
      getters: {
        'getters/getCurrentUser': 'from user'
      },
      actions: {
        'actions/SENDUSERCONFIRMATION': 'from user'
      }
    })
  })

  it('renders UnconfirmedAccountBanner component', () => {
    const wrapper = shallowMount(UnconfirmedAccountBanner, { store, localVue, vuetify })
    expect(wrapper).toMatchSnapshot()
  })
})
