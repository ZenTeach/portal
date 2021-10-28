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
        'Atoms and elements': {
          'Atoms are made up of protons, neutrons and electrons': {
            progress: '1/2',
            feedback: ['Look at this image of an atom.']
          },
          'Electrons circle the nucleus.': {
            progress: '0/1',
            feedback: ['Look at this image of an atom.']
          },
          'Protons and neutrons are located inside the nucleus.': {
            progress: '0/1',
            feedback: ['Look at this image of an atom.']
          },
          'Protons and neutrons have a mass of 1.': {
            progress: '1/1',
            feedback: ['Look at this image of an atom.']
          },
          'Electrons have a mass of 0.': {
            progress: '1/1',
            feedback: ['Look at this image of an atom.']
          }
        }
      },
      {
        'Charges and Ions': {
          'Two electrons or two protons repel each other.': {
            progress: '1/1',
            feedback: 'This video explains electron shells quite nicely.'
          },
          'Atoms have a neutral charge.': {
            progress: '0/1',
            feedback: 'Revise theses lesson slides.'
          },
          'All atoms want to achieve a full outer shell (usually 8 electrons)': {
            progress: '0/1',
            feedback: 'This video explains electron shells quite nicely.'
          }
        }
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
