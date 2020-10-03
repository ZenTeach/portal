import Vue from 'vue'
import { sync } from 'vuex-router-sync'
import VueCookies from 'vue-cookies'
import vuetify from '@/plugins/vuetify'
import '@/plugins'
import App from '@/App.vue'
import router from './src/router'
import store from '@/store'
import moment from 'moment'

Vue.config.productionTip = true
Vue.use(VueCookies)

const unsync = sync(store, router)

Vue.filter('formatDate', function (value) {
  if (value) {
    return moment(String(value)).format('DD/MM/YYYY')
  }
})

var vm = new Vue({
  router,
  store,
  vuetify,
  render: h => h(App)
}).$mount('#app')

window._vm = vm
unsync()
