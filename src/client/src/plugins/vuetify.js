import '@mdi/font/css/materialdesignicons.css'
import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import 'vuetify/dist/vuetify.css'

Vue.use(Vuetify)

const opts = {
  icons: {
    iconfont: 'md'
  },
  theme: {
    themes: {
      light: {
        primary: '#8bc34a',
        secondary: '#009688',
        accent: '#03a9f4',
        error: '#f44336',
        warning: '#ffeb3b',
        info: '#2196f3',
        success: '#4caf50'
      }
    }
  }
}

export default new Vuetify(opts)
