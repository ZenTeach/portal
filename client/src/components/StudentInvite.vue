<template>
  <v-dialog v-model="dialog" max-width="500px" max-height="450px">
              <ValidationObserver ref="observer" v-slot="{ invalid, validated, passes }">
              <v-card>
                <v-card-title>
                  <span class="headline">Invite a student</span>
                </v-card-title>

                <v-card-text>
                  <v-container>
                    <v-row>
                      <v-col cols="10" lg="12" sm="9" md="12">
                        <ValidationProvider rules="required" name="firstname">
                        <v-text-field label="First name" v-model="firstname" outlined grow></v-text-field>
                        </ValidationProvider>

                        <ValidationProvider rules="required" name="lastname">
                        <v-text-field label="Last name" v-model="lastname" outlined grow></v-text-field>
                        </ValidationProvider>

                        <ValidationProvider rules="required|email" name="email" v-slot="{ errors }">
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
                      </v-col>
                    </v-row>
                  </v-container>
                </v-card-text>

                <v-card-actions>
                  <div class="flex-grow-1"></div>
                  <v-btn color="blue darken-1" text @click="closeDialog()" outlined>Cancel</v-btn>
                  <v-btn color="blue darken-1" text outlined :disabled="invalid || !validated" @click="passes(inviteStudent)">Save</v-btn>
                </v-card-actions>
              </v-card>
              </ValidationObserver>
            </v-dialog>
</template>

<script>
import {
  ValidationObserver,
  ValidationProvider
} from 'vee-validate'
import { createNamespacedHelpers } from 'vuex'
const { mapActions } = createNamespacedHelpers('classrooms')
export default {
  name: 'StudentInvite',
  components: {
    ValidationObserver,
    ValidationProvider
  },
  props: {
    classId: {
      type: Number,
      required: true
    },
    dialogController: {
      type: Boolean,
      required: true
    }
  },
  inject: ['eventBus'],
  computed: {
    ...mapActions({ INVITESTUDENT: 'INVITE_STUDENT' }),
    dialog () {
      return this.dialogController
    }
  },
  data: () => ({
    menu: false,
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
      this.eventBus.$emit('toggle-invite-dialog', false)
    },
    closeDialog () {
      this.eventBus.$emit('toggle-invite-dialog', false)
    }
  }
}
</script>

<style scoped>

</style>
