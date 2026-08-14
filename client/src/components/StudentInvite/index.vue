<template>
  <v-dialog v-model="dialog" max-width="60vw" max-height="65vh">
    <v-card>
        <v-tabs background-color="primary darken-1" centered>
          <v-tab key="singleStudentInvite">Invite a student</v-tab>
          <v-tab key="multiStudentInvite">Invite multiple students</v-tab>
          <v-tab-item key="singleStudentInvite">
            <StudentInviteInfo :classId="classId"/>
          </v-tab-item>
          <v-tab-item key="multiStudentInvite">
            <StudentInviteMutliInsert :classId="classId"/>
          </v-tab-item>
        </v-tabs>
        <v-divider></v-divider>
    </v-card>
  </v-dialog>
</template>

<script>
import {
  ValidationObserver
} from 'vee-validate'
import StudentInviteInfo from './form'
import StudentInviteMutliInsert from './multi-insert'
import { createNamespacedHelpers } from 'vuex'
import Vue from 'vue'
const { mapActions } = createNamespacedHelpers('classrooms')
export default {
  name: 'StudentInvite',
  components: {
    ValidationObserver,
    StudentInviteInfo,
    StudentInviteMutliInsert
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
  provide () {
    return {
      childEvents: this.childEvents
    }
  },
  computed: {
    ...mapActions({ INVITESTUDENT: 'INVITE_STUDENT' }),
    dialog () {
      return this.dialogController
    }
  },
  mounted: function () {
    this.childEvents.$on('toggle-dialog', this.closeDialog)
  },
  data: () => ({
    studentInvite: [],
    menu: false,
    childEvents: new Vue()
  }),
  methods: {
    closeDialog () {
      this.eventBus.$emit('toggle-invite-dialog', false)
    }
  }
}
</script>

<style scoped>

</style>
