import Vue from 'vue'
import { createLocalVue, mount } from '@vue/test-utils'
import QuizViewPrompt from '@/components/QuizViewComponents/QuizViewPrompt'
import Vuetify from 'vuetify'
import lodash from 'lodash'
import VueLodash from 'vue-lodash'

Vue.use(Vuetify)
const localVue = createLocalVue()
let vuetify

describe('QuizViewPrompt.vue', () => {
  beforeEach(() => {
    vuetify = new Vuetify()
    localVue.use(VueLodash, { name: 'custom', lodash: lodash })
  })

  it('renders QuizViewPrompt component', () => {
    const wrapper = mount(QuizViewPrompt, {
      localVue,
      vuetify,
      propsData: {
        showDialog: true,
        showSessionErrors: false,
        error: {},
        loading: false,
        proceedAction: () => {}
      }
    })
    expect(wrapper).toMatchSnapshot()
  })
  it('emits an email update event on input', async () => {
    const wrapper = mount(QuizViewPrompt, {
      localVue,
      vuetify,
      propsData: {
        showDialog: true,
        showSessionErrors: false,
        error: {},
        loading: false,
        proceedAction: () => {}
      }
    })
    const emailInput = wrapper.find('input')
    emailInput.element.value = 'atestemail@example.com'
    await emailInput.trigger('input')

    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('update:email')[0]).toEqual([
      'atestemail@example.com'
    ])
  })
})
