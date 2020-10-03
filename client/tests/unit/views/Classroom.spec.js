import Vue from 'vue'
import { createLocalVue, shallowMount } from '@vue/test-utils'
import Classroom from '@/views/Classroom'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { Store } from 'vuex-mock-store'

Vue.use(VueRouter)
Vue.use(Vuetify)
const localVue = createLocalVue()
const router = new VueRouter()

xdescribe('Classroom.vue', () => {
  let vuetify
  let $store

  beforeEach(() => {
    vuetify = new Vuetify()
    $store = new Store({
      state: {
        classrooms: {
          value: 'from classrooms'
        }
      },
      getters: {
        'classrooms/getter': jest.fn()
      }
    })
  })

  it.skip('renders correctly', () => {
    const wrapper = shallowMount(Classroom, { localVue, vuetify, router, mocks: { $store } })
    expect(wrapper).toMatchSnapshot()
  })
})
