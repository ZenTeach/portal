<template>
  <v-alert
    v-bind="$attrs"
    :elevation="elevation"
    :value="value"
    :dark="dark"
    v-on="$listeners"
    id="notification_alert"
  >
    <slot />
    <template v-slot:append v-if="appStatus === 'error'">
      <v-btn
        @click="showErrorUserFeedback"
      >
        Send Feedback
      </v-btn>
    </template>
  </v-alert>
</template>

<script>
import { showReportDialog } from '@sentry/browser'
import { createNamespacedHelpers } from 'vuex'

const { mapGetters } = createNamespacedHelpers('user')
const { mapGetters: appGetters } = createNamespacedHelpers('app')

export default {
  name: 'MaterialNotification',

  inheritAttrs: false,

  props: {
    dark: {
      type: Boolean,
      default: true
    },
    elevation: {
      type: [Number, String],
      default: 6
    },
    value: {
      type: Boolean,
      default: true
    }
  },
  computed: {
    ...mapGetters({
      currentUser: 'getCurrentUser'
    }),
    ...appGetters({
      appStatus: 'statusText'
    })
  },
  created: function () {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  },
  mounted: function () {
    window.setTimeout(this.toggleOffError, 5000)
  },
  methods: {
    showErrorUserFeedback () {
      // console.log('Showing sentry error dialog!')
      const dialogOpts = {
        eventId: window.crypto.randomUUID(),
        user: {
          email: this.currentUser.email,
          name: this.currentUser.firstname + ' ' + this.currentUser.lastname
        },
        title: 'Error Report',
        subtitle: 'Please describe the problem you experienced'
      }
      showReportDialog(dialogOpts)
    },
    toggleOffError () {
      this.$store.dispatch('app/TOGGLE_ERROR', {}, { root: true })
      this.$store.dispatch('app/TOGGLE_APP_STATUS', '', { root: true })
    }
  }
}
</script>
