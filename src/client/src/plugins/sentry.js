import Vue from 'vue'
import * as Sentry from '@sentry/browser';
import { Vue as VueIntegration, CaptureConsole } from '@sentry/integrations';

var sentry_dsn = process.env.VUE_APP_SENTRY_DSN
Sentry.init({
  dsn: `${sentry_dsn}`,
  integrations: [new VueIntegration({Vue, attachProps: true})]
});
