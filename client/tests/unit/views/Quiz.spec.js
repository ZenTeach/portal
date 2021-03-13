import { shallowMount, createLocalVue } from '@vue/test-utils'
import Quiz from '@/views/Quiz.vue'
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

describe('Quiz.vue', () => {
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
          quiz_questions: [],
          subject: '',
          uuid: '',
          has_started: false,
          has_submitted: false,
          report_card: [],
          graded_quizzes: []
        }
      },
      getters: {
        'getters/gradedQuizzes': 'from quiz',
        'getters/uuid': 'from quiz'
      },
      actions: {
        'actions/LOAD_QUIZ': 'from quiz',
        'actions/FETCH_GRADEDQUIZZES': 'from quiz',
        'actions/SENDSTUDENTREPORTCARD': 'from quiz'
      }
    })
    mockStore.state.quiz.graded_quizzes = []
  })

  it('matches snapshot', () => {
    mockStore.getters.uuid = jest.fn()
    const wrapper = shallowMount(Quiz, { store, localVue, vuetify, router, mocks: { $store: mockStore } })
    expect(wrapper).toMatchSnapshot()
  })
})
