import { shallowMount, createLocalVue } from '@vue/test-utils'
import QuestionSearchResult from '@/components/QuestionSearchResult'
import Vuetify from 'vuetify'
import Vue from 'vue'

Vue.use(Vuetify)
const localVue = createLocalVue()

describe('QuestionSearchResult.vue Test', () => {
  let vuetify
  let props
  beforeEach(() => {
    vuetify = new Vuetify()
    props = {
      resultSet: []
    }
  })
  it('renders empty search result component', () => {
    const wrapper = shallowMount(QuestionSearchResult, { localVue, vuetify, propsData: props })
    expect(wrapper.element).toMatchSnapshot()
  })
})
