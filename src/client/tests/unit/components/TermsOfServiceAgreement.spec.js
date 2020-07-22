import { shallowMount, createLocalVue } from '@vue/test-utils'
import TermsOfServiceAgreement from '@/components/TermsOfServiceAgreement'
import Vuetify from 'vuetify'
import Vue from 'vue'

Vue.use(Vuetify)
const localVue = createLocalVue()

describe('TermsOfServiceAgreement.vue Test', () => {
  let vuetify
  beforeEach(() => {
    vuetify = new Vuetify()
  })

  it('renders TOS component', () => {
    const wrapper = shallowMount(TermsOfServiceAgreement, { localVue, vuetify })
    expect(wrapper.element).toMatchSnapshot()
  })
})
