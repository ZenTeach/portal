import Vue from 'vue'
import StudentList from '@/components/StudentList'
import { createLocalVue, shallowMount } from '@vue/test-utils'
import Vuetify from 'vuetify'

Vue.use(Vuetify)
const localVue = createLocalVue()
const students = [
  {
    classes: [
      '/api/v1/school_class/12'
    ],
    email: 'peter.griffin@example.com',
    firstname: 'peter',
    id: 10,
    lastname: 'griffin'
  },
  {
    classes: [
      '/api/v1/school_class/12'
    ],
    email: 'jmama@example.com',
    firstname: 'Joe',
    id: 11,
    lastname: 'Mama'
  },
  {
    classes: [
      '/api/v1/school_class/12'
    ],
    email: 'cnsksnajkd@cnjaksbcas.anjdk',
    firstname: 'cankcldnal',
    id: 12,
    lastname: 'csnjklasdjals'
  },
  {
    classes: [
      '/api/v1/school_class/12'
    ],
    email: 'cahnkas@cnjaskjas.cnajs',
    firstname: 'acnjkna',
    id: 13,
    lastname: 'cnasdcoankdlas'
  }
]
describe('StudentList.vue', () => {
  let vuetify
  let $mockEventBus

  beforeEach(() => {
    $mockEventBus = new Vue()
    vuetify = new Vuetify()
  })

  it('renders correctly', () => {
    const wrapper = shallowMount(StudentList, {
      localVue,
      vuetify,
      props: {
        students: students
      },
      provide: {
        eventBus () {
          return $mockEventBus
        }
      }
    })
    expect(wrapper).toMatchSnapshot()
  })
})
