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
    toggleManualInviteDialog () {
      this.dialog = true
    }
  }
}
</script>

<style>
</style>
