<template>
    <v-content>
    <v-container fluid fill-height>
      <v-layout align-center justify-center>
        <v-flex xs12 sm10 md6>
          <ValidationObserver ref="observer" v-slot="{ invalid, validated }" >
          <v-card class="elevation-3">
            <v-toolbar color="grey lighten-3" text>
              <v-toolbar-title class="d-flex text-center">
                <span class="font-weight-light">Zen</span>
                <span class>Teach</span>
                <span class="mx-1">Account Recovery</span>
              </v-toolbar-title>
              <v-spacer></v-spacer>
            </v-toolbar>
            <v-card-text>
              <v-form>
                <ValidationProvider rules="required|email" name="email" v-slot="{errors}">
                <v-text-field
                  v-model="email"
                  :error-messages="errors"
                  label="Email"
                  placeholder
                  prepend-icon="email"
                  outline
                  required
                ></v-text-field>
                </ValidationProvider>
              </v-form>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn
                :disabled="invalid || !validated"
                color="primary lighten-2"
                class="mr-4"
                @click="recover_account"
                outlined>Reset Password</v-btn>
            </v-card-actions>
            <v-spacer></v-spacer>
          </v-card>
          </ValidationObserver>
        </v-flex>
      </v-layout>
    </v-container>
  </v-content>
</template>

<script>

import {
  ValidationObserver,
  ValidationProvider
} from 'vee-validate'

export default {
  name: 'AccountRecovery',
  components: {
    ValidationProvider,
    ValidationObserver
  },
  data: () => {
    return {
      valid: true,
      email: ''
    }
  },
  methods: {
    validate () {
      return this.$refs.observer.validate()
    },
    recover_account () {
      if (this.validate) {
        this.$store.dispatch(
          'user/SENDACCOUNTRECOVERY', this.email, { root: true }
        )
      }
    }
  }
}
</script>
