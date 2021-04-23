import Vue from 'vue'
import Vuetify from 'vuetify'
import Classrooms from '@/views/Classrooms'
import { createLocalVue, shallowMount } from '@vue/test-utils'
import { Store } from 'vuex-mock-store'

Vue.use(Vuetify)
const localVue = createLocalVue()

describe('Classrooms.vue', () => {
  let vuetify
  let $store

  beforeEach(() => {
    vuetify = new Vuetify()
    $store = new Store({
      state: {
        classrooms: {
          class_list: 'from classrooms',
          current_class: 'from classrooms'
        },
        app: {
        }
      },
      getters: {
        'getters/CLASSLIST': 'from classrooms'
        // getSubjects: jest.fn(() => {
        //   [
        //     { id: 1, name: 'Chemistry', enabled: true, remarks: '' },
        //     { id: 2, name: 'Biology', enabled: true, remarks: '' },
        //     { id: 3, name: 'Physics', enabled: true, remarks: '' }
        //   ]
        // })
      },
      actions: {
        'actions/GETCLASSES': 'from classrooms',
        'actions/CREATECLASS': 'from classrooms'
      }
    })
  })

  xit('renders correctly', () => {
    const wrapper = shallowMount(Classrooms, {
      localVue,
      vuetify,
      mocks: { $store: $store }
    })
    expect(wrapper).toMatchSnapshot()
  })
})
