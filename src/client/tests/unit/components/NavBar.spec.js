import { shallowMount, createLocalVue } from '@vue/test-utils'
import Vuex from 'vuex'
import NavBar from '@/components/NavBar.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'

Vue.use(Vuex)
Vue.use(Vuetify)
const localVue = createLocalVue()

describe('NavBar.vue', () => {
  let actions
  let store
  beforeEach(() => {
    actions = {
      SIGNOUT_USER: jest.fn()
    }
    store = new Vuex.Store({
      modules: {
        user: {
          actions
        }
      }
    })
  })

  it('renders component', () => {
    const wrapper = shallowMount(NavBar, { store, localVue })
    expect(wrapper).toMatchSnapshot()
  })
})
