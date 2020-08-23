import { shallowMount, createLocalVue } from '@vue/test-utils'
import Quiz from '@/views/Quiz.vue'
import VueRouter from 'vue-router'
import Vuex from 'vuex'

const localVue = createLocalVue()
localVue.use(Vuex)
localVue.use(VueRouter)
const router = new VueRouter()

describe('Quiz.vue', () => {
  let store

  beforeEach(() => {
    store = new Vuex.Store({})
  })
  it.skip('has renders the view correctly', () => {
    const wrapper = shallowMount(Quiz, { store, localVue, router })
    expect(wrapper.isVueInstance()).toBe(true)
  })
})
