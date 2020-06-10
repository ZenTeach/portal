<template>
  <div>
    <v-data-table
          :headers="headers"
          :items="students"
          :expand="expand"
          item-key="name"
        >
        <template v-slot:items="props">
          <tr @click="props.expanded = !props.expanded">
            <td class="text-xs-right">{{ props.item.firstname }}</td>
            <td class="text-xs-right">{{ props.item.lastname }}</td>
            <td class="text-xs-right">{{ props.item.email }}</td>
          </tr>
        </template>
        <template v-slot:footer>
          <v-menu offset-y>
            <template v-slot:activator="{ on }">
              <v-btn color="primary" right fab dark class="ma-2 pa-2" v-on="on">
                <v-icon>mdi-plus</v-icon>
              </v-btn>
            </template>
            <v-list>
              <v-list-item @click="toggleFileInviteDialog" >
                <v-list-item-title> Import from csv </v-list-item-title>
              </v-list-item>

              <v-list-item @click="toggleManualInviteDialog" >
                <v-list-item-title> Add manually </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>

          <v-dialog
            v-model="fileSelectorDialog"
            max-width="500px"
            transition="dialog-transition"
          >
          <v-card>
            <v-card-title>
              <span class="headline">Select a file:</span>
            </v-card-title>
            <v-card-text>
              <template>
                <v-file-input v-model="selectedFile" show-size accept=".csv" label="Select a csv input"></v-file-input>
              </template>
            </v-card-text>
            <v-card-actions>
              <v-btn @click="importStudents"> Import </v-btn>
              <v-btn @click="fileSelectorDialog = false"> Cancel</v-btn>
            </v-card-actions>
          </v-card>
          </v-dialog>

          <student-invite :dialogController="dialog" :classId="classId"/>
        </template>

      </v-data-table>
  </div>
</template>

<script>
import StudentInvite from '@/components/StudentInvite'
import Vue from 'vue'

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
    headers: [
      { text: 'First name', align: 'left', value: 'firstname', width: 20 },
      { text: 'Last Name', align: 'left', value: 'lastname', width: 20 },
      { text: 'Email', align: 'left', value: 'email', width: 30 },
      { text: 'Report card', align: 'right', value: '', width: 30 }
    ],
    fileSelectorDialog: false,
    dialog: false,
    eventBus: new Vue()
  }),
  methods: {
    toggleInviteDialog (data) {
      this.dialog = data
    },
    importStudents () {
      this.fileSelectorDialog = false
      const formData = new FormData()
      const csrfCookie = this.$cookies.get('access_csrf_token')
      console.log('CSRF access cookie', csrfCookie)
      formData.append('files', this.selectedFile, this.selectedFile.name)
      this.$store.dispatch('classrooms/IMPORTSTUDENTSFROMCSV', { classId: this.classId, formData: formData, headerData: csrfCookie }, { root: true })
        .then(response => {
          this.$store.dispatch('classrooms/GETCURRENTCLASS', this.classId, { root: true })
        })
    },
    toggleFileInviteDialog () {
      this.fileSelectorDialog = true
    },
    toggleManualInviteDialog () {
      this.dialog = true
    }
  }
}
</script>

<style>
</style>
