import '@mdi/font/css/materialdesignicons.css'
import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import 'vuetify/dist/vuetify.css'

Vue.use(Vuetify)

const opts = {
  icons: {
    iconfont: 'md'
  }
}

export default new Vuetify(opts)
