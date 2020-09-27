import { shallowMount, createLocalVue } from '@vue/test-utils'
import ChangePassword from '@/views/ChangePassword.vue'
import VueRouter from 'vue-router'
import Vuex from 'vuex'
import Vue from 'vue'
import Vuetify from 'vuetify'

Vue.use(Vuetify)
const localVue = createLocalVue()
localVue.use(Vuex)
localVue.use(VueRouter)
const router = new VueRouter()

describe('ChangePassword.vue', () => {
  let vuetify
  let store

  beforeEach(() => {
    store = new Vuex.Store({})
    vuetify = new Vuetify()
  })
  it('has renders the view correctly', () => {
    const wrapper = shallowMount(ChangePassword, { store, localVue, vuetify, router })
    expect(wrapper).toMatchSnapshot()
  })
})
