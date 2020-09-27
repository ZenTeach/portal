import Vue from 'vue'
import * as Sentry from '@sentry/browser'
import { Vue as VueIntegration } from '@sentry/integrations'

var sentryDsn = process.env.VUE_APP_SENTRY_DSN
Sentry.init({
  dsn: `${sentryDsn}`,
  integrations: [new VueIntegration({ Vue, attachProps: true })]
})
