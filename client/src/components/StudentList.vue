<template>
  <div>
    <v-data-table
          :headers="headers"
          :items="students"
          :expand="expand"
          item-key="name"
        >
        <template v-slot:item.confirmed="{ item }">
          <v-tooltip left v-if="item.confirmed === true" >
            <template v-slot:activator="{ on, attrs }">
              <v-icon v-bind="attrs"
                v-on="on"
                color="success darken-1" >
                mdi-account-check
              </v-icon>
            </template>
            <span>Account email is verified!</span>
          </v-tooltip>

          <v-tooltip left v-else>
            <template v-slot:activator="{ on, attrs }">
              <v-icon
                color="warning darken-1"
                v-bind="attrs"
                v-on="on">
                mdi-account-clock
              </v-icon>
            </template>
            <span>Email hasn't been confirmed yet!</span>
          </v-tooltip>

        </template>
        <template v-slot:items="props">
          <tr>
            <td class="text-xs-right">{{ props.item.firstname }}</td>
            <td class="text-xs-right">{{ props.item.lastname }}</td>
            <td class="text-xs-right">{{ props.item.email }}</td>
          </tr>
        </template>
        <template v-slot:item.actions="{ item }">
            <v-icon
              medium
              @click="showConfirmItemDelete(item)"
            >
              mdi-trash-can-outline
            </v-icon>
            <v-icon
              medium
              @click="showEditItemDialog(item)"
            >
              mdi-pencil-circle
            </v-icon>
            <v-icon
              medium
              @click="sendStudentConfirmationEmail(item.id)"
              :disabled="item.confirmed"
            >
              mdi-email-send
            </v-icon>
        </template>
        <template v-slot:footer>
          <v-menu offset-y>
            <template v-slot:activator="{ on }">
              <v-btn color="primary" right dark class="ma-4 pa-2" v-on="on">
                <v-icon>mdi-plus</v-icon> Add a student
              </v-btn>
            </template>
            <v-list>
              <v-list-item @click="toggleManualInviteDialog" >
                <v-list-item-title> Add manually </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>

          <student-invite :dialogController="dialog" :classId="classId"/>
        </template>

      </v-data-table>
      <v-dialog
        v-model="deleteConfirmationModal"
        persistent :overlay="false"
        max-width="500px"
        transition="dialog-transition"
      >
        <v-card class="d-flex flex-column align-left pa-3">
          <v-card-title primary-title>
            <h3 class="title font-weight-bold mb-2">
              Confirm student deletion
            </h3>
          </v-card-title>
          <v-card-text>
            <p class="font-weight-medium body-1 ">
              This action will remove the student from the classroom and in effect remove all
              quiz performance data. Are you sure to delete a student from your classroom?
            </p>
        </v-card-text>
        <v-card-actions class="justify-space-between px-5">
            <v-btn color="error" @click="deleteItem(studentToBeDeleted)" class="mr-4" >Delete</v-btn>
            <v-btn color="secondary" outlined class="mr-4" @click.native.prevent="hideConfirmItemDelete()">Cancel</v-btn>
        </v-card-actions>
        </v-card>
      </v-dialog>

      <v-dialog
        persistent
        v-model="editStudentModal"
        :overlay="false"
        max-width="500px"
        transition="dialog-transition">
          <v-card class="d-flex flex-column align-left pa-3">
            <v-card-title primary-title>
              <h3 class="title font-weight-bold mb-2">
                Edit student data
              </h3>
            </v-card-title>
            <v-card-text>
              <v-container>
                <v-row>
                  <v-col>
                    <v-text-field
                      v-model="updatedEmail"
                      label="Email"
                      :placeholder="editableEmail"
                      prepend-icon="email"
                      outline
                      required
                    ></v-text-field>
                  </v-col>
                </v-row>
              </v-container>
            </v-card-text>
            <v-card-actions class="justify-space-between px-5">
                <v-btn color="primary" @click="editItem()" class="mr-4" >Update</v-btn>
                <v-btn color="error" outlined class="mr-4" @click.native.prevent="hideEditStudentDialog()">Cancel</v-btn>
            </v-card-actions>
          </v-card>
      </v-dialog>
  </div>
</template>

<script>
import StudentInvite from '@/components/StudentInvite'
import { createNamespacedHelpers } from 'vuex'
import Vue from 'vue'

const { mapActions } = createNamespacedHelpers('classrooms')

export default {
  name: 'StudentList',
  components: {
    StudentInvite
  },
  props: {
    students: Array
  },
  provide () {
    return {
      eventBus: this.eventBus
    }
  },
  mounted: function () {
    this.eventBus.$on('toggle-invite-dialog', this.toggleInviteDialog)
  },
  computed: {
    classId () {
      return parseInt(this.$route.params.id)
    }
  },
  data: () => ({
    expand: false,
    selectedFile: null,
    deleteConfirmationModal: false,
    studentToBeDeleted: null,
    editableEmail: '',
    updatedEmail: '',
    editStudentModal: false,
    headers: [
      { text: 'Status', align: 'right', value: 'confirmed', width: 10 },
      { text: 'First name', align: 'left', value: 'firstname', width: 20 },
      { text: 'Last Name', align: 'left', value: 'lastname', width: 20 },
      { text: 'Email', align: 'left', value: 'email', width: 30 },
      { text: '', align: 'right', value: 'actions', width: 50 }
    ],
    fileSelectorDialog: false,
    dialog: false,
    eventBus: new Vue()
  }),
  methods: {
    ...mapActions({
      removeStudent: 'REMOVESTUDENTFROMCLASS',
      updateStudentEmail: 'UPDATESTUDENTEMAIL',
      sendStudentConfirmationEmail: 'SENDSTUDENTCONFIRMATIONEMAIL'
    }),
    toggleInviteDialog (data) {
      this.dialog = data
    },
    toggleManualInviteDialog () {
      this.dialog = true
    },
    showConfirmItemDelete (item) {
      this.deleteConfirmationModal = true
      this.studentToBeDeleted = item.id
    },
    hideConfirmItemDelete (item) {
      this.deleteConfirmationModal = false
    },
    showEditItemDialog (item) {
      this.editableEmail = item.email
      this.editStudentModal = true
    },
    hideEditStudentDialog () {
      this.editStudentModal = false
      this.editableEmail = ''
    },
    deleteItem (item) {
      this.removeStudent({
        classId: this.classId,
        studentId: item
      })
      this.deleteConfirmationModal = false
      this.studentToBeDeleted = null
    },
    editItem () {
      const payload = {
        old_email: this.editableEmail,
        new_email: this.updatedEmail
      }

      this.updateStudentEmail(
        {
          classId: this.classId,
          data: payload
        }
      )

      this.hideEditStudentDialog()
    }
  }
}
</script>

<style>
</style>
