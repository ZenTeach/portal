import Vue from 'vue'
import StudentInvite from '@/components/StudentInvite'
import { createLocalVue, shallowMount } from '@vue/test-utils'
import Vuetify from 'vuetify'
import { Store } from 'vuex-mock-store'

Vue.use(Vuetify)
const localVue = createLocalVue()

describe('StudentInvite.vue', () => {
  let vuetify
  let $store
  let $mockEventBus

  beforeEach(() => {
    $mockEventBus = new Vue()
    vuetify = new Vuetify()
    $store = new Store({
      state: {
        classrooms: {
          class_list: 'from classrooms',
          current_class: 'from classrooms'
        }
      },
      getters: {
        'getters/CLASSLIST': 'from classrooms'
      },
      actions: {
        'actions/INVITE_STUDENT': 'from classrooms',
        'actions/CREATECLASS': 'from classrooms'
      }
    })
  })

  it('renders correctly', () => {
    const wrapper = shallowMount(StudentInvite, {
      localVue,
      vuetify,
      props: {
        classId: 1,
        dialogController: true
      },
      mocks: { $store: $store },
      provide: {
        eventBus () {
          return $mockEventBus
        }
      }
    })
    expect(wrapper).toMatchSnapshot()
  })
})
