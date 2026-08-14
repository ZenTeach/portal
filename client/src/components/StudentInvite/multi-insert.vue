<script>
import {
  ValidationObserver,
  ValidationProvider
} from 'vee-validate'
export default {
  name: 'StudentInviteMutliInsert',
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
    multiStudentEmail: ''
  }),
  methods: {
    inviteStudents () {
      const studentInfo = this.multiStudentEmail.split('\n').map((student) => {
        const [firstname, lastname, email] = student.split(' ')
        return {
          firstname: firstname,
          lastname: lastname,
          email: email,
          classId: this.classId
        }
      })
      const promises = studentInfo.map((studentInvite) => {
        return this.$store.dispatch('classrooms/INVITE_STUDENT', studentInvite, { root: true })
      })
      Promise.allSettled(promises).then((results) => {
        this.childEvents.$emit('toggle-dialog', false)
      })
    },
    closeDialog () {
      this.childEvents.$emit('toggle-dialog', false)
    }
  }
}
</script>
<template>
  <v-card>
    <ValidationObserver ref="multiInsertObserver" v-slot="{ invalid, validated, passes }">
      <div class="d-flex flex-column justify-start align-center">
        <v-container fluid>
          <v-row>
            <div class="mx-3">
              <span class="headline">Invite multiple student</span>
            </div>
          </v-row>
          <v-row>
            <v-col cols="12" lg="12" sm="12" md="12">
              <ValidationProvider rules="required" name="studentsList" v-slot="{ errors }">
                <v-textarea
                  clearable
                  clear-icon="mdi-close-circle"
                  label="Enter Student details"
                  placeholder="Jake Mulligam jmulligam@oxfordacademy.ac.uk"
                  v-model="multiStudentEmail"
                  :error-messages="errors"
                  class="text-body-2"
                  outlined
                  required
                ></v-textarea>
              </ValidationProvider>
            </v-col>
          </v-row>
        </v-container>
      </div>
      <v-card-actions>
        <div class="flex-grow-1"></div>
        <v-btn color="blue darken-1" text @click="closeDialog()" outlined>Cancel</v-btn>
        <v-btn color="blue darken-1" text outlined :disabled="invalid || !validated" @click="passes(inviteStudents)">Save</v-btn>
      </v-card-actions>
    </ValidationObserver>
  </v-card>
</template>
