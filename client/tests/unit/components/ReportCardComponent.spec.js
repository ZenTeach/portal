import { shallowMount, createLocalVue } from '@vue/test-utils'
import ReportCardComponent from '@/components/ReportCardComponent'
import Vuetify from 'vuetify'
import Vue from 'vue'

Vue.use(Vuetify)
const localVue = createLocalVue()

describe('ReportCardComponent.vue Test', () => {
  let vuetify
  beforeEach(() => {
    vuetify = new Vuetify()
  })

  const propsData = {
    reports: [
      {
        topic: 'Atoms and elements',
        knowledge_item: [
          'Atoms are made up of protons, neutrons and electrons',
          'Electrons circle the nucleus.',
          'Protons and neutrons are located inside the nucleus.',
          'Protons and neutrons have a mass of 1.',
          'Electrons have a mass of 0.'
        ],
        progress: [
          '1/2',
          '0/1',
          '0/1',
          '1/1',
          '1/1'
        ],
        feedback: [
          'Look at this image of an atom.',
          'Look at this image of an atom.',
          'Look at this image of an atom.',
          'Look at this image of an atom.',
          'Look at this image of an atom.'
        ]
      },
      {
        topic: 'Charges and Ions',
        knowledge_item: [
          'Two electrons or two protons repel each other.',
          'Atoms have a neutral charge.',
          'All atoms want to achieve a full outer shell (usually 8 electrons)'
        ],
        progress: [
          '1/1',
          '0/1',
          '0/1'
        ],
        feedback: [
          'This video explains electron shells quite nicely.',
          'Revise theses lesson slides.',
          'This video explains electron shells quite nicely.'
        ]
      }]
  }

  it('renders component with data', () => {
    const wrapper = shallowMount(ReportCardComponent, { localVue, vuetify, propsData: propsData })
    expect(wrapper.element).toMatchSnapshot()
  })

  it('renders component without data', () => {
    const emptyProps = {
      reports: []
    }
    const wrapper = shallowMount(ReportCardComponent, { localVue, vuetify, propsData: emptyProps })
    const elem = wrapper.find('h3')
    expect(elem.text()).toEqual('Report card has not been processed yet!')
  })
})
