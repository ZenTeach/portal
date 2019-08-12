import Vue from 'vue'
import './plugins/vuetify'
import App from './App.vue'
import router from './router'
import AuthPlugin from './plugins/auth'
import store from './store'
import VueQrcodeReader from 'vue-qrcode-reader'

Vue.config.productionTip = false
Vue.use(AuthPlugin)
Vue.use(VueQrcodeReader)

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
