import { mount, shallowMount, createLocalVue } from '@vue/test-utils'
import Signup from '@/views/Signup.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import flushPromises from 'flush-promises'

Vue.use(Vuex)
Vue.use(Vuetify)

const localVue = createLocalVue()

describe('Signup.vue Tests', () => {
  let actions
  let $store
  let vuetify

  beforeEach(() => {
    jest.useFakeTimers()
    vuetify = new Vuetify()
    actions = {
      REGISTER_USER: jest.fn()
    }

    $store = new Vuex.Store({
      modules: {
        user: {
          actions
        }
      }
    })
  })

  it('renders a Signup form', () => {
    const wrapper = shallowMount(Signup, { localVue, mocks: { $store } })
    expect(wrapper.element).toMatchSnapshot()
  })

  it.skip('checks form Validity', async () => {
    // const wrapper = shallowMount(Signup, { localVue, mocks: { $store, sync: false }})
    const wrapper = mount(Signup, { localVue, vuetify, mocks: { $store }, sync: false })
    wrapper.vm.$ref.firstname_input.setValue('')
    await flushPromises()
    jest.runAllTimers()
    expect(wrapper.find('.error')).toBeTruthy()
  })

  // it('')
})
