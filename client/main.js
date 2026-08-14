import Vue from 'vue'
import { sync } from 'vuex-router-sync'
import VueCookies from 'vue-cookies'
import vuetify from '@/plugins/vuetify'
import 'chartist/dist/chartist.min.css'
import { createAuth0 } from '@auth0/auth0-vue'

import '@/plugins'
import App from '@/App.vue'
import router from './src/router'
import store from '@/store'
import VueLodash from 'vue-lodash'
import lodash from 'lodash'
import moment from 'moment'

Vue.config.productionTip = true
Vue.use(VueCookies)
Vue.use(VueLodash, { name: 'custom', lodash: lodash })
Vue.use(require('vue-chartist'), {
  messageNoData: 'You have not enough data',
  classNoData: 'empty'
})

// auth0 config
const auth0Client = createAuth0({
  domain: 'dev-iogpmb3i.eu.auth0.com',
  client_id: 'guIMJsBvSKsmdJPUHtujKxPKQUjaT4cp',
  redirect_uri: window.location.origin
})
Vue.use(auth0Client)
// Global date filter
Vue.filter('formatDate', function (value) {
  if (!value) return ''
  if (value) {
    return moment(String(value)).format('DD/MM/YYYY')
  }
})
const unsync = sync(store, router)

var vm = new Vue({
  router,
  store,
  vuetify,
  render: h => h(App)
}).$mount('#app')

window._vm = vm
unsync()
