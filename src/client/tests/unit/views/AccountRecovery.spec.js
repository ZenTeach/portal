import { shallowMount, createLocalVue } from '@vue/test-utils'
import AccountRecovery from '@/views/AccountRecovery.vue'
import VueRouter from 'vue-router'
import Vuex from 'vuex'
import Vue from 'vue'
import Vuetify from 'vuetify'

Vue.use(Vuetify)
const localVue = createLocalVue()
localVue.use(Vuex)
localVue.use(VueRouter)
const router = new VueRouter()

describe('AccountRecovery.vue', () => {
  let vuetify
  let store

  beforeEach(() => {
    store = new Vuex.Store({})
    vuetify = new Vuetify()
  })
  it('has renders the view correctly', () => {
    const wrapper = shallowMount(AccountRecovery, { store, localVue, vuetify, router })
    expect(wrapper).toMatchSnapshot()
  })
})
