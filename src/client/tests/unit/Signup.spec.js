import { shallowMount, createLocalVue } from '@vue/test-utils'
import Signup from '@/views/Signup.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import { ValidationObserver, ValidationProvider } from 'vee-validate'

Vue.use(Vuetify)
const localVue = createLocalVue()
localVue.component('ValidationObserver', ValidationObserver)
localVue.use(Vuex)
localVue.component('ValidationProvider', ValidationProvider)

describe('Signup.vue Tests', () => {
  const userRegisterAction = jest.fn()
  let store
  let $router
  let vuetify

  beforeEach(() => {
    jest.useFakeTimers()
    vuetify = new Vuetify()
    $router = {
      push: jest.fn()
    }
    store = new Vuex.Store({
      modules: {
        user: {
          namespaced: true,
          actions: {
            REGISTER_USER: userRegisterAction
          }
        }
      }
    })
  })

  it('renders a Signup form', () => {
    const wrapper = shallowMount(Signup, { localVue })
    expect(wrapper.element).toMatchSnapshot()
  })

  it('checks form Validity', async () => {
    const wrapper = shallowMount(Signup, { localVue, store, vuetify, mocks: { $router }, sync: false })
    wrapper.setData({
      firstname: 'Joe',
      lastname: 'Mama',
      email: 'joe.mama@example.com',
      password: 'Asdfgh123456!',
      passwordConfirmation: 'Asdfgh123456!',
      dob: '01/01/1970',
      legal_checkbox: true
    })
    wrapper.vm.checkValidity = jest.fn(() => true)
    expect(wrapper.vm.checkValidity()).toBeTruthy()
    wrapper.vm.processSignup()
    await wrapper.vm.$nextTick()
    expect(userRegisterAction).toHaveBeenCalled()
  })
})
