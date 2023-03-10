<script>
import {
  ValidationObserver,
  ValidationProvider
} from 'vee-validate'
export default {
  name: 'StudentInviteInfo',
  components: {
    ValidationObserver,
    ValidationProvider
  },
  inject: ['childEvents'],
  props: {
    classId: {
      type: Number,
      required: true
    }
  },
  data: () => ({
    firstname: '',
    lastname: '',
    email: ''
  }),
  methods: {
    inviteStudent () {
      const payload = {
        classId: this.classId,
        firstname: this.firstname,
        lastname: this.lastname,
        email: this.email
      }
      this.$store.dispatch('classrooms/INVITE_STUDENT', payload, { root: true })
      this.childEvents.$emit('toggle-dialog', false)
    },
    closeDialog () {
      this.childEvents.$emit('toggle-dialog', false)
    }
  }
}
</script>
<template>
  <v-card>
    <ValidationObserver ref="singleInsertObserver" v-slot="{ invalid, validated, passes }">
      <div class="d-flex flex-column justify-start align-center">
        <v-container fluid>
          <v-row>
            <div class="mx-3">
              <span class="headline">Invite a student</span>
            </div>
          </v-row>
          <v-row>
            <v-col cols="4" lg="4" sm="4" md="4">
              <ValidationProvider rules="required" name="firstname">
              <v-text-field label="First name" v-model="firstname" class="text-body-2" outlined grow></v-text-field>
              </ValidationProvider>
            </v-col>
            <v-col cols="4" lg="4" sm="4" md="4">
              <ValidationProvider rules="required" name="lastname">
              <v-text-field label="Last name" v-model="lastname" class="text-body-2" outlined grow></v-text-field>
              </ValidationProvider>
            </v-col>
            <v-col cols="4" lg="4" sm="4" md="4">
              <ValidationProvider rules="required|email" name="email" v-slot="{ errors }">
                <v-text-field
                  v-model="email"
                  :error-messages="errors"
                  label="Email"
                  placeholder
                  class="text-body-2"
                  prepend-icon="email"
                  outlined
                  required
                ></v-text-field>
              </ValidationProvider>
            </v-col>
          </v-row>
        </v-container>
      </div>
      <v-card-actions>
        <div class="flex-grow-1"></div>
        <v-btn color="blue darken-1" text @click="closeDialog()" outlined>Cancel</v-btn>
        <v-btn color="blue darken-1" text outlined :disabled="invalid || !validated" @click="passes(inviteStudent)">Save</v-btn>
      </v-card-actions>
    </ValidationObserver>
  </v-card>
</template>
