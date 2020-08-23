import { shallowMount, createLocalVue } from '@vue/test-utils'
import Vuex from 'vuex'
import MaterialCard from '@/components/MaterialCard.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'

Vue.use(Vuetify)
Vue.use(Vuex)
const localVue = createLocalVue()

describe('MaterialCard.vue', () => {
  let vuetify

  beforeEach(() => {
    vuetify = new Vuetify()
  })

  it('renders component', () => {
    const wrapper = shallowMount(MaterialCard, {
      localVue,
      vuetify,
      props: {
        title: 'Some title',
        text: 'Some text'
      }
    })
    expect(wrapper).toMatchSnapshot()
  })
})
