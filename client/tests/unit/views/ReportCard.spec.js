import { shallowMount, createLocalVue } from '@vue/test-utils'
import ReportCard from '@/views/ReportCard.vue'
import VueRouter from 'vue-router'
import Vuex from 'vuex'
import Vue from 'vue'
import Vuetify from 'vuetify'
import { Store } from 'vuex-mock-store'

Vue.use(Vuetify)
Vue.use(VueRouter)
const localVue = createLocalVue()
localVue.use(Vuex)
const router = new VueRouter()

describe('ReportCard.vue', () => {
  let store
  let vuetify
  let mockStore

  beforeEach(() => {
    vuetify = new Vuetify()
    mockStore = new Store({
      state: {
        app: {
          loggedIn: 'from app',
          error: 'from app'
        },
        quiz: {
          report_card: []
        }
      },
      getters: {
        'getters/reportCard': 'from quiz',
        'getters/uuid': 'from quiz'
      },
      actions: {
        'actions/LOAD_QUIZ': 'from quiz',
        'actions/FETCH_REPORTCARD': 'from quiz'
      }
    })
  })

  it('matches snapshot', () => {
    const wrapper = shallowMount(ReportCard, { store, localVue, vuetify, router, mocks: { $store: mockStore } })
    expect(wrapper).toMatchSnapshot()
  })
})
