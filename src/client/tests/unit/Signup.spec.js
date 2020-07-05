import { mount, shallowMount, createLocalVue } from '@vue/test-utils'
import Signup from '@/views/Signup.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import flushPromises from 'flush-promises'
import { ValidationObserver, ValidationProvider, extend } from 'vee-validate'
import { required, email, max, min, confirmed } from 'vee-validate/dist/rules'
Vue.use(Vuex)
Vue.use(Vuetify)

const localVue = createLocalVue()
localVue.component('ValidationObserver', ValidationObserver)
localVue.component('ValidationProvider', ValidationProvider)

describe('Signup.vue Tests', () => {
  let actions
  let $store
  let vuetify

  beforeEach(() => {
    extend('required', {
      ...required,
      message: 'This field is required'
    })

    extend('max', {
      ...max,
      message: 'This field must be {length} characters or less'
    })

    extend('min', {
      ...min,
      message: 'This {_field_} must be greater that {length} characters or less'
    })

    extend('confirmed', {
      ...confirmed,
      message: 'This {_field_} should not be different from {_target_}.'
    })

    extend('email', {
      ...email,
      message: 'This field must be a valid email'
    })

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

  it('checks form Validity', async () => {
    const wrapper = mount(Signup, { localVue, vuetify, mocks: { $store }, sync: false })
    wrapper.find('input').setValue('')
    await flushPromises()
    expect(wrapper.find('.error')).toBeTruthy()
  })
})
