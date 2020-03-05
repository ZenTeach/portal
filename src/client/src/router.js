import Vue from "vue";
import Router from "vue-router";
import store from "./store";
Vue.use(Router);

const router = new Router({
  mode: "history",
  base: process.env.BASE_URL,
  routes: [
    {
      path: "/login",
      name: "login",
      component: () => import(/* webpackChunkName: "Login" */ "./views/Login")
    },
    {
      path: "/signup",
      name: "signup",
      component: () => import(/* webpackChunkName: "Signup" */ "./views/Signup")
    },
    {
      path: "/",
      name: "Dashboard",
      component: () =>
        import(/* webpackChunkName: "Dashboard" */ "./views/Dashboard"),
      meta: {
        requiresAuth: true
      }
    },
    {
      path: "/classroom/:id",
      name: "Classroom",
      component: () =>
        import(/* webpackChunkName: "Classroom" */ "./views/Classroom"),
      meta: {
        requiresAuth: true
      }
    },
    {
      path: "/classrooms",
      name: "Classrooms",
      component: () =>
        import(/* webpackChunkName: "Classrooms" */ "./views/Classrooms"),
      meta: {
        requiresAuth: true
      }
    },
    {
      path: "/quiz/:id",
      name: "Quiz",
      component: () => import(/* webpackChunkName: "Quiz" */ "./views/Quiz"),
      meta: {
        requiresAuth: true
      }
    },
    {
      path: "/students",
      name: "Student List",
      component: () =>
        import(/* webpackChunkName: "Students" */ "./views/Students"),
      meta: {
        requiresAuth: true
      }
    }
  ]
});

router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (store.state.app.loggedIn) {
      next();
    } else {
      router.push("/login");
    }
  }
  next();
});

export default router;
