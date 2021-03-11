import Vue from 'vue'
import * as Sentry from '@sentry/vue'

var sentryDsn = process.env.VUE_APP_SENTRY_DSN
Sentry.init({
  dsn: `${sentryDsn}`,
  Vue: Vue
})
