<template>
    <v-card
        class="d-flex align-left pa-3"
    >
      <ValidationObserver ref="observer" v-slot="{ invalid, validated }">
        <div class="px-3" color="primary">
          <h4 class="title font-weight-bold mb-2">
              Send an Invite
          </h4>
          <p class="category font-weight-light mb-0">
              Tell your friends about Zenteach
          </p>
        </div>
        <v-card-text>
            <v-form>
                <ValidationProvider rules="required|email" name="firstname" v-slot="{ errors }">
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
        <v-card-actions class="justify-space-between px-5">
            <v-btn :disabled="invalid || !validated" color="primary" @click="processInvite()" class="mr-4" >Send Invitation</v-btn>
            <v-btn color="error" outlined class="mr-4" @click.native.prevent="closeInviteDialog()">Cancel</v-btn>
        </v-card-actions>
      </ValidationObserver>
    </v-card>
</template>

<script>

import MaterialCard from '@/components/MaterialCard'
import {
  ValidationObserver,
  ValidationProvider
} from 'vee-validate'

export default {
  name: 'InviteUser',
  components: {
    ValidationObserver,
    ValidationProvider,
    MaterialCard
  },
  data: function () {
    return {
      email: ''
    }
  },
  methods: {
    isFormValid () {
      return this.$refs.observer.validate()
    },
    closeInviteDialog () {
      this.email = ''
      this.$store.commit('app/TOGGLE_APP_INVITE_MODAL')
    },
    processInvite () {
      if (this.isFormValid()) {
        this.$store.dispatch('user/SENDUSERINVITE', this.email)
      }
    }
  }
}
</script>
