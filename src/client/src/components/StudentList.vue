<template>
  <div>
    <v-data-table
          :headers="headers"
          :items="students"
          :expand="expand"
          item-key="name"
        >
        <template v-slot:items="props">
          <tr>
            <td class="text-xs-right">{{ props.item.firstname }}</td>
            <td class="text-xs-right">{{ props.item.lastname }}</td>
            <td class="text-xs-right">{{ props.item.email }}</td>
          </tr>
        </template>
        <template v-slot:item.actions="{ item }">
            <v-icon
              large
              @click="deleteItem(item)"
            >
              mdi-trash-can-outline
            </v-icon>
        </template>
        <template v-slot:footer>
          <v-menu offset-y>
            <template v-slot:activator="{ on }">
              <v-btn color="primary" right fab dark class="ma-2 pa-2" v-on="on">
                <v-icon>mdi-plus</v-icon>
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
    headers: [
      { text: 'First name', align: 'left', value: 'firstname', width: 20 },
      { text: 'Last Name', align: 'left', value: 'lastname', width: 20 },
      { text: 'Email', align: 'left', value: 'email', width: 30 },
      { text: '', align: 'right', value: 'actions', width: 30 }
    ],
    fileSelectorDialog: false,
    dialog: false,
    eventBus: new Vue()
  }),
  methods: {
    ...mapActions({
      removeStudent: 'REMOVESTUDENTFROMCLASS'
    }),
    toggleInviteDialog (data) {
      this.dialog = data
    },
    toggleManualInviteDialog () {
      this.dialog = true
    },
    deleteItem (item) {
      console.log(item.id)
      this.removeStudent({
        classId: this.classId, 
        studentId: item.id
      })
      // this.$store.dispatch('classrooms/REMOVESTUDENTFROMCLASS', [this.classId, item.id], {root: true})
    }
  }
}
</script>

<style>
</style>
