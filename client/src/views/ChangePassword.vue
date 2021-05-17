<template>
    <v-content>
    <v-container fluid fill-height>
      <v-layout align-center justify-center>
        <v-flex xs12 sm10 md6>
          <ValidationObserver ref="observer" v-slot="{ invalid, validated }" >
          <v-card class="elevation-3">
            <v-toolbar color="grey lighten-3" flat>
              <v-toolbar-title class="d-flex text-center">
                <span class="font-weight-light">Zen</span>
                <span class>Teach</span>
                <span class="mx-1">Update Password</span>
              </v-toolbar-title>
              <v-spacer></v-spacer>
            </v-toolbar>
            <v-card-text>
              <v-form>
                <ValidationProvider rules="required|min:12" name="password" v-slot="{errors}" vid="password">
                <v-text-field
                  id="password"
                  v-model="password"
                  ref="password"
                  :error-messages="errors"
                  label="Password"
                  name="password"
                  prepend-icon="lock"
                  outline
                  required
                  type="password"
                ></v-text-field>
                </ValidationProvider>

                <ValidationProvider rules="required|confirmed:password" name="passwordConfirmation" v-slot="{errors}">
                <v-text-field
                  id="password-confirmation"
                  v-model="passwordConfirmation"
                  :error-messages="errors"
                  label="Confirm Password"
                  name="password_confirmation"
                  prepend-icon="lock"
                  outline
                  required
                  type="password"
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
                @click="update_password"
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
  computed: {
    token () {
      return this.$route.query.token
    },
    email () {
      return this.$route.query.email
    }
  },
  data: () => {
    return {
      valid: true,
      password: '',
      passwordConfirmation: ''
    }
  },
  methods: {
    validate: function () {
      return this.$refs.observer.validate() || this.token || this.email
    },
    update_password () {
      if (this.validate) {
        this.$store.dispatch(
          'user/UPDATEUSERPASSWORD', {
            token: this.token,
            email: this.email,
            password: this.password
          }, { root: true }
        )
      }
    }
  }
}
</script>
