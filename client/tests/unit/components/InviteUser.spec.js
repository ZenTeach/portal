import Vue from 'vue'
import { createLocalVue, shallowMount } from '@vue/test-utils'
import InviteUser from '@/components/InviteUser'
import Vuetify from 'vuetify'
import { Store } from 'vuex-mock-store'
import Vuex from 'vuex'

Vue.use(Vuetify)
const localVue = createLocalVue()
localVue.use(Vuex)

describe('InviteUser.vue', () => {
  let vuetify
  let store
  beforeEach(() => {
    vuetify = new Vuetify()
    store = new Store({
      state: {
        app: {
          inviteModalVisible: 'from app'
        }
      },
      mutations: {
        'mutations/TOGGLE_APP_INVITE_MODAL': 'from app'
      },
      actions: {
        'actions/SENDUSERINVITE': 'from app'
      }
    })
  })

  it('renders InviteUser component', () => {
    const wrapper = shallowMount(InviteUser, { store, localVue, vuetify })
    expect(wrapper).toMatchSnapshot()
  })
})
