<template>
    <v-banner
        single-line
        v-model="visible"
        color="yellow lighten-4"
    >
        <div class="d-flex justify-space-between justify-space-around align-baseline">
            <div class="display-2" style="max-width: 60vw;">
                <span class="d-flex">
                    <v-icon
                        slot="icon"
                        color="red"
                        size="36"
                    >
                    mdi-account-alert-outline
                    </v-icon>
                    <p class="ma-3 font-weight-bold d-inline">Account not verified.</p>
                </span>
                    <hr />
                <div>
                    <p class="text-lighten-3 font-weight-light text-wrap subtitle-2">Please confirm your account to continue using the portal. Check your Spam folder for the confirmation email. If you haven't recieved it yet, click 'Resend email' to receive it.</p>
                </div>
            </div>
            <div class="mr-10">
                <v-btn :loading="loading" :disabled="loading" @click="sendConfirmationEmail" icon color="success" >
                    <v-icon size="16">
                        mdi-refresh
                    </v-icon>
                    Resend
                    <template v-slot:loader>
                        <span class="custom-loader">
                        <v-icon light>mdi-cached</v-icon>
                        </span>
                    </template>
                </v-btn>
            </div>
        </div>

    </v-banner>
</template>

<script>

import { createNamespacedHelpers } from 'vuex'

const { mapActions, mapGetters } = createNamespacedHelpers('user')

export default {
  name: 'UnconfirmedAccountBanner',
  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      loading: false
    }
  },
  methods: {
    ...mapGetters({
      currentUser: 'getCurrentUser'
    }),
    ...mapActions({
      sendConfirmation: 'SENDUSERCONFIRMATION'
    }),
    sendConfirmationEmail () {
      this.loading = true
      const { email } = this.currentUser()
      this.sendConfirmation(email).then(
        this.loading = false
      )
    }
  }
}
</script>

<style scoped>

.custom-loader {
    animation: loader 1s infinite;
    display: flex;
  }
  @-moz-keyframes loader {
    from {
      transform: rotate(0);
    }
    to {
      transform: rotate(360deg);
    }
  }
  @-webkit-keyframes loader {
    from {
      transform: rotate(0);
    }
    to {
      transform: rotate(360deg);
    }
  }
  @-o-keyframes loader {
    from {
      transform: rotate(0);
    }
    to {
      transform: rotate(360deg);
    }
  }
  @keyframes loader {
    from {
      transform: rotate(0);
    }
    to {
      transform: rotate(360deg);
    }
  }
</style>
