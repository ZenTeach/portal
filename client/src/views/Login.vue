<template>
  <v-content>
    <v-container fluid fill-height>
      <v-layout align-center justify-center>
        <v-flex xs12 sm10 md6>
          <div>
            <button @click="login">Log in</button>
          </div>
        </v-flex>
      </v-layout>
    </v-container>
  </v-content>
</template>

<script>
import { createNamespacedHelpers } from 'vuex'

const { mapGetters } = createNamespacedHelpers('app')

export default {
  name: 'Login',
  data: () => ({
    valid: true,
    email: '',
    emailRules: [
      v => !!v || 'E-mail is required',
      v => /.+@.+\..+/.test(v) || 'E-mail must be valid'
    ],
    password: '',
    checkbox: false,
    lazy: false
  }),
  computed: {
    ...mapGetters({
      loading: 'loading'
    })
  },
  methods: {
    login () {
      this.$auth0.loginWithRedirect()
    }
  }
}
</script>
