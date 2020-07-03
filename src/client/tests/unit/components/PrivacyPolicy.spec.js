import { shallowMount, createLocalVue } from '@vue/test-utils'
import PrivacyPolicy from '@/components/PrivacyPolicy'
import Vuetify from 'vuetify'
import Vue from 'vue'

Vue.use(Vuetify)
const localVue = createLocalVue()

describe('PrivacyPolicy.vue Test', () => {
  let vuetify
  beforeEach(() => {
    vuetify = new Vuetify()
  })
  it('renders TOS component', () => {
    const wrapper = shallowMount(PrivacyPolicy, { localVue, vuetify })
    expect(wrapper.element).toMatchSnapshot()
  })
})
