import Vue from 'vue'
import Vuetify from 'vuetify'
import Questions from '@/views/Questions'
import { createLocalVue, shallowMount } from '@vue/test-utils'
import { Store } from 'vuex-mock-store'

Vue.use(Vuetify)
const localVue = createLocalVue()

describe('Questions.vue', () => {
  let vuetify
  let $store
  let props

  beforeEach(() => {
    vuetify = new Vuetify()
    $store = new Store({
      state: {
        questions: {
          questions: 'from questions'
        }
      },
      getters: {
        'getters/QUESTIONLIST': 'from questions'
      },
      actions: {
        'actions/GETQUESTIONS': 'from questions'
      }
    })
    props = {
      resultSet: []
    }
  })

  it('renders correctly', () => {
    const wrapper = shallowMount(Questions, { localVue, vuetify, mocks: { $store: $store }, propsData: props })
    expect(wrapper).toMatchSnapshot()
  })
})
