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
        requiresAuth: true
      }
    },
    {
      path: '/classroom/:id',
      name: 'Classroom',
      component: () =>
        import(/* webpackChunkName: "Classroom" */ './views/Classroom'),
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/classrooms',
      name: 'Classrooms',
      component: () =>
        import(/* webpackChunkName: "Classrooms" */ './views/Classrooms'),
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/quiz/:id',
      name: 'Quiz',
      component: () => import(/* webpackChunkName: "Quiz" */ './views/Quiz'),
      meta: {
        quizView: true
      }
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
      path: '/quiz_view/:id',
      name: 'Quiz View',
      component: () =>
        import(/* webpackChunkName: "QuizView" */ './views/QuizView')
    },
    {
      path: '/report_card/:uuid',
      name: 'Student Report Card',
      component: () =>
        import(/* webpackChunkName: "QuizView" */ './views/ReportCard')
    },
    {
      path: '/tos',
      name: 'Terms Of Service',
      component: () =>
        import(/* webpackChunkName: "TOSView" */ './views/TOS')
    },
    {
      path: '/privacy_policy',
      name: 'Privacy Policy',
      component: () =>
        import(/* webpackChunkName: "PrivacyPolicyView" */ './views/PrivacyPolicy')
    },
    {
      path: '/recover_account',
      name: 'Recover Account',
      component: () =>
        import(/* webpackChunkName: "AccountRecoveryView" */ './views/AccountRecovery')
    },
    {
      path: '/change_password',
      name: 'Change Password',
      component: () =>
        import(/* webpackChunkName: "ChangePasswordView" */ './views/ChangePassword')
    },
    {
      path: '/confirm_account',
      name: 'Confirm Account',
      component: () =>
        import(/** webpackChunkName: "ConfirmAccountView" */ './views/AccountConfirmation')
    }
  ]
})

router.beforeEach((to, from, next) => {
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
