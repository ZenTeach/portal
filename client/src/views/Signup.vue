<template>
  <v-main>
    <v-container fluid fill-height>
      <v-layout align-center justify-center>
        <v-flex xs12 sm10 md6>
          <ValidationObserver ref="observer" v-slot="{ invalid, validated }">
          <v-card class="elevation-3">
            <v-toolbar color="grey lighten-3" text>
              <v-toolbar-title>Signup</v-toolbar-title>
              <v-spacer></v-spacer>
            </v-toolbar>
            <v-card-text>
              <v-form>
                <ValidationProvider rules="required" name="firstname" v-slot="{ errors }">
                <v-text-field
                  v-model="firstname"
                  label="Firstname"
                  :error-messages="errors"
                  placeholder
                  prepend-icon="person"
                  outline
                  required
                ></v-text-field>
                </ValidationProvider>

                <ValidationProvider rules="required" name="lastname" v-slot="{errors}">
                <v-text-field
                  v-model="lastname"
                  label="Lastname"
                  placeholder
                  :error-messages="errors"
                  prepend-icon="person"
                  outline
                  required
                ></v-text-field>
                </ValidationProvider>

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

                <v-menu
                  ref="menu"
                  v-model="date_picker_menu"
                  :close-on-content-click="false"
                  :return-value.sync="dob"
                  transition="scale-transition"
                  offset-y
                  min-width="290px"
                >
                  <template v-slot:activator="{ on }">
                    <ValidationProvider rules="required" name="dob" v-slot="{errors}">
                    <v-text-field
                      v-model="dob"
                      label="Date of Birth"
                      :error-messages="errors"
                      prepend-icon="event"
                      readonly
                      v-on="on"
                      outline
                    ></v-text-field>
                    </ValidationProvider>
                    </template>
                    <v-date-picker v-model="dob" no-title scrollable min="1950-01-01">
                      <div class="flex-grow-1"></div>
                      <v-btn text color="primary" @click="date_picker_menu = false">Cancel</v-btn>
                      <v-btn
                        text
                        color="primary"
                        @click="$refs.menu.save(dob)"
                      >OK</v-btn>
                    </v-date-picker>
                </v-menu>

                <ValidationProvider rules="required|min:8" name="password" v-slot="{errors}" vid="password">
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

                <ValidationProvider rules="required|confirmed:password" name="Password Confirmation" v-slot="{errors}">
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

                <ValidationProvider rules="required" name="invite_code" v-slot="{errors}">
                <v-text-field
                  v-model="invite_code"
                  label="Invite code"
                  placeholder
                  :error-messages="errors"
                  prepend-icon="mdi-account-key"
                  type="text"
                  outline
                  required
                ></v-text-field>
                </ValidationProvider>
                <ValidationProvider :rules="{ required: { allowFalse: false } }" name="TosAndPrivacyPolicyAgreement" v-slot="{errors}">
                  <v-checkbox
                    v-model="legal_checkbox"
                    color="deep-purple"
                    :error-messages="errors"
                    required
                  >
                    <template v-slot:label>
                      <p class="d-sm-inline">
                      I agree to the&nbsp;
                      <a href="#" @click.stop.prevent="tos_dialog = true">Terms of Service</a>
                      &nbsp;and&nbsp;
                      <a href="#" @click.stop.prevent="privacy_policy_dialog = true">Privacy Policy</a>*
                      </p>
                    </template>
                  </v-checkbox>
                </ValidationProvider>
              </v-form>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn :disabled="invalid || !validated" color="primary lighten-2" outlined class="mr-4" @click="processSignup">Signup</v-btn>
            </v-card-actions>
            <v-spacer></v-spacer>
            <v-dialog
              v-model="tos_dialog"
              absolute
              max-width="800"
            >
              <terms-of-service-agreement />
            </v-dialog>
            <v-dialog
              v-model="privacy_policy_dialog"
              absolute
              max-width="800"
            >
              <privacy-policy />
            </v-dialog>
          </v-card>
          </ValidationObserver>
        </v-flex>
      </v-layout>
    </v-container>
  </v-main>
</template>

<script>

import {
  ValidationObserver,
  ValidationProvider
} from 'vee-validate'
import TermsOfServiceAgreement from '@/components/TermsOfServiceAgreement'
import PrivacyPolicy from '@/components/PrivacyPolicy'
import { createNamespacedHelpers } from 'vuex'

const { mapActions } = createNamespacedHelpers('user')

export default {
  name: 'Signup',
  components: {
    ValidationProvider,
    ValidationObserver,
    TermsOfServiceAgreement,
    PrivacyPolicy
  },
  data () {
    return {
      valid: true,
      email: '',
      firstname: '',
      lastname: '',
      dob: null,
      password: '',
      passwordConfirmation: '',
      invite_code: '',
      checkbox: false,
      lazy: false,
      tos_dialog: false,
      privacy_policy_dialog: false,
      legal_checkbox: false,
      date_picker_menu: false
    }
  },
  methods: {
    ...mapActions({ registerUser: 'REGISTER_USER' }),
    checkValidity () {
      return this.$refs.observer.validate()
    },
    processSignup () {
      if (this.checkValidity) {
        this.registerUser(
          {
            firstname: this.firstname,
            lastname: this.lastname,
            email: this.email,
            password: this.password,
            date_of_birth: this.dob,
            invitation_code: this.invite_code,
            role: 'Teacher'
          })
      }
    }
  }
}
</script>
