import Vue from 'vue'
import { sync } from 'vuex-router-sync'
import VueCookies from 'vue-cookies'
import vuetify from '@/plugins/vuetify'
import '@/plugins'
import App from '@/App.vue'
import router from './src/router'
import store from '@/store'
import VueLodash from 'vue-lodash'
import lodash from 'lodash'

Vue.config.productionTip = true
Vue.use(VueCookies)
Vue.use(VueLodash, { name: 'custom', lodash: lodash })

const unsync = sync(store, router)

var vm = new Vue({
  router,
  store,
  vuetify,
  render: h => h(App)
}).$mount('#app')

window._vm = vm
unsync()
