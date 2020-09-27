import { shallowMount, createLocalVue } from '@vue/test-utils'
import Vuex from 'vuex'
import HelperOffset from '@/components/HelperOffset.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'

Vue.use(Vuex)
Vue.use(Vuetify)
const localVue = createLocalVue()

describe('HelperOffset.vue', () => {
  let vuetify

  beforeEach(() => {
    vuetify = new Vuetify()
  })

  it('renders component', () => {
    const wrapper = shallowMount(HelperOffset, {
      localVue,
      vuetify
    })
    expect(wrapper).toMatchSnapshot()
  })
})
