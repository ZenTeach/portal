import Vue from 'vue'
import Router from 'vue-router'
import store from './store'

Vue.use(Router)

const router = new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import(/* webpackChunkName: "Login" */ './views/Login')
    },
    {
      path: '/signup',
      name: 'signup',
      component: () => import(/* webpackChunkName: "Signup" */ './views/Signup')
    },
    {
      path: '/',
      name: 'Dashboard',
      component: () =>
        import(/* webpackChunkName: "Dashboard" */ './views/Dashboard'),
      meta: {
        requiresAuth: true,
        breadcrumb: 'Dashboard'
      }
    },
    {
      path: '/classrooms',
      name: 'Classrooms',
      component: () =>
        import(/* webpackChunkName: "Classrooms" */ './views/Classrooms'),
      meta: {
        requiresAuth: true,
        breadcrumb: 'Classrooms'
      },
      children: [
        {
          path: '/classroom/:id',
          name: 'Classroom',
          component: () =>
            import(/* webpackChunkName: "Classroom" */ './views/Classroom'),
          meta: {
            requiresAuth: true,
            breadcrumb: 'Classroom'
          },
          children: [
            {
              path: '/quiz/:uuid',
              name: 'Quiz',
              component: () =>
                import(/* webpackChunkName: "Quiz" */ './views/Quiz'),
              meta: {
                quizView: true,
                breadcrumb: 'Quiz'
              }
            }
          ]
        }
      ]
    },
    {
      path: '/quiz_view/:id',
      name: 'Quiz View',
      component: () =>
        import(/* webpackChunkName: "QuizView" */ './views/QuizView')
    },
    {
      path: '/post_submit/:quiz_uuid',
      name: 'Quiz Submit View',
      component: () =>
        import(
          /* webpackChunkName: "QuizSubmit" */ './views/QuizSubmitView'
        )
    },
    {
      path: '/students',
      name: 'Student List',
      component: () =>
        import(/* webpackChunkName: "Students" */ './views/Students'),
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/report_card/:uuid',
      name: 'Student Report Card',
      component: () =>
        import(/* webpackChunkName: "ReportCard" */ './views/ReportCard'),
      meta: {
        breadcrumb: 'Report Card'
      }
    },
    {
      path: '/tos',
      name: 'Terms Of Service',
      component: () => import(/* webpackChunkName: "TOSView" */ './views/TOS')
    },
    {
      path: '/privacy_policy',
      name: 'Privacy Policy',
      component: () =>
        import(
          /* webpackChunkName: "PrivacyPolicyView" */ './views/PrivacyPolicy'
        )
    },
    {
      path: '/recover_account',
      name: 'Recover Account',
      component: () =>
        import(
          /* webpackChunkName: "AccountRecoveryView" */ './views/AccountRecovery'
        )
    },
    {
      path: '/change_password',
      name: 'Change Password',
      component: () =>
        import(
          /* webpackChunkName: "ChangePasswordView" */ './views/ChangePassword'
        )
    },
    {
      path: '/confirm_account',
      name: 'Confirm Account',
      component: () =>
        import(
          /* webpackChunkName: "ConfirmAccountView" */ './views/AccountConfirmation'
        )
    },
    {
      path: '/confirm_student_account',
      name: 'Confirm Student Account',
      component: () =>
        import(
          /* webpackChunkName: "ConfirmStudentAccountView" */ './views/ConfirmStudentAccount'
        )
    },
    {
      path: '/user-profile',
      name: 'User Profile',
      component: () =>
        import(/* webpackChunkName: "UserProfileView" */ './views/UserProfile'),
      meta: {
        requiresAuth: true,
        breadcrumb: 'Profile'
      }
    },
    {
      path: '/questions',
      name: '',
      component: () =>
        import(/* webpackChunkName: "QuestionsView" */ './views/Questions'),
      meta: {
        requiresAuth: true,
        breadcrumb: 'Question Library'
      }
    },
    {
      path: '/question/create',
      name: 'Create a question',
      component: () =>
        import(
          /* webpackChunkName: "QuestionCreateView" */ './views/QuestionCreate'
        ),
      meta: {
        requiresAuth: true,
        breadcrumb: 'Create a question (Multiple Choice)'
      }
    },
    {
      path: '/question/edit',
      name: 'Edit question',
      component: () =>
        import(
          /* webpackChunkName: "QuestionCreateView" */ './views/QuestionEdit'
        ),
      meta: {
        requiresAuth: true,
        breadcrumb: 'Edit question (Multiple Choice)'
      }
    },
    {
      path: '*',
      name: 'NotFound',
      component: () =>
        import(/* webpackChunkName: 'NotFoundView' */ './views/NotFound')
    }
  ]
})

router.beforeEach((to, _from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (store.state.app.loggedIn) {
      next()
    } else {
      router.push('/login')
    }
  }
  next()
})

export default router
