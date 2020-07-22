import { shallowMount, createLocalVue } from '@vue/test-utils'
import App from '@/App.vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import Vue from 'vue'
import { Store } from 'vuex-mock-store'
import VueRouter from 'vue-router'

Vue.use(VueRouter)
Vue.use(Vuetify)
const localVue = createLocalVue()
localVue.use(Vuex)

describe('App.vue', () => {
  let vuetify
  let mockStore
  const routes = [{
    path: '/',
    component: { render: h => '-' }
  }]
  const router = new VueRouter({
    routes
  })
  beforeEach(() => {
    vuetify = new Vuetify()

    mockStore = new Store({
      state: {
        app: {
          loggedIn: 'from app',
          error: 'from app'
        }
      },
      actions: {
        'actions/FETCHCURRENTUSER': 'from user'
      }
    })
  })

  it('matches snapshot', () => {
    const wrapper = shallowMount(App, { localVue, vuetify, router, mocks: { $store: mockStore } })
    expect(wrapper).toMatchSnapshot()
  })

  it("has 'drawer' set to true", () => {
    const wrapper = shallowMount(App, { localVue, vuetify, router, mocks: { $store: mockStore } })
    expect(wrapper.vm.drawer).toBeFalsy()
  })

  it("dispatches 'FETCHCURRENTUSER' action with each mount", () => {
    // eslint-disable-next-line no-unused-vars
    const wrapper = shallowMount(App, { localVue, vuetify, router, mocks: { $store: mockStore } })
    expect(mockStore.dispatch).toHaveBeenCalled()
    expect(mockStore.dispatch).toHaveBeenCalledWith('user/FETCHCURRENTUSER', {}, { root: true })
  })
})
