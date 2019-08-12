import Vue from 'vue'
import '@/client/plugins/vuetify'
import App from '@/client/App.vue'
import router from '@/client/router'
import AuthPlugin from '@/client/plugins/auth'
import store from '@/client/store'
import VueQrcodeReader from 'vue-qrcode-reader'

Vue.config.productionTip = false
Vue.use(AuthPlugin)
Vue.use(VueQrcodeReader)

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
