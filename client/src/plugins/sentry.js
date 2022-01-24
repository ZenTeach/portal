import Vue from 'vue'
import * as Sentry from '@sentry/browser'

var sentryDsn = process.env.VUE_APP_SENTRY_DSN
Sentry.init({
  dsn: `${sentryDsn}`,
  Vue: Vue,
  enabled: true,
  trackComponents: true
})
