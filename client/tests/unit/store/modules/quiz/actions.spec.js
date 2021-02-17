import actions from '@/store/modules/quiz/actions'
// import { fetchGradedReportCards } from '@/service/quiz_service'
import { Store } from 'vuex-mock-store'
// import { loginUser } from '@/service/teacher_auth'

const { FETCH_GRADEDQUIZZES } = actions

const mockStore = new Store({
  state: {
    quiz: {
      quiz_questions: [],
      subject: '',
      uuid: '',
      has_started: false,
      has_submitted: false,
      report_card: [],
      graded_quizzes: []
    }
  },
  mutations: {
    'app/TOGGLE_APP_LOADING': 'from app',
    'app/TOGGLE_ERROR': 'from app',
    'quiz/UNSET_GRADEDQUIZZES': 'from quiz',
    'quiz/SET_GRADEDQUIZZES': 'from quiz'
  },
  // getters: {
  //   'user/getCurrentUser': 'from user'
  // },
  actions: {
    // 'actions/LOGIN_USER': 'from user',
    // 'actions/SIGNOUT_USER': 'from user',
    // 'actions/REGISTER_USER': 'from user',
    'actions/FETCH_GRADEDQUIZZES': 'from quiz'
  }
})

jest.mock('@/service/quiz_service')

describe('Quiz actions', () => {
  const data = {
    data: [{
      grade_breakdown: [
        {
          feedback: [
            'Look at these images.',
            'Look at these images.',
            'Revise theses lesson slides.'
          ],
          knowledge_item: [
            'MASS',
            'MASS',
            'NEUTRON MASS AND CHARGE'
          ],
          progress: [
            '0/1',
            '0/1',
            '0/1'
          ],
          topic: 'Atomic Structure'
        },
        {
          feedback: [
            'Look at these images.'
          ],
          knowledge_item: [
            'DEFINITION MIXTURE'
          ],
          progress: [
            '0/1'
          ],
          topic: 'Chemical Bonds'
        }
      ],
      score: 3,
      student: {
        classes: [
          '/api/v1/school_class/42'
        ],
        email: 'peter.griffin@example.com',
        firstname: 'peter',
        id: 42,
        lastname: 'griffin'
      },
      uuid: 'a8196676-efd3-475e-8308-90eca5a90618'
    }]
  }

  let fetchGradedReportCardsMock

  beforeAll(() => {
    jest.clearAllMocks()
    fetchGradedReportCardsMock = jest.mock('@/service/quiz_service').fn('fetchGradedReportCards')
  })
  xit('executes FETCH_GRADEDQUIZZES', () => {
    const quizId = 5
    fetchGradedReportCardsMock.mockImplementationOnce(() => Promise.resolve({ data: data }))
    FETCH_GRADEDQUIZZES(mockStore, quizId)
    expect(mockStore.commit).toHaveBeenCalledTimes(4)
  })
})
