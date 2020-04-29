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
            <td><router-link to="/report_card/1">Report card</router-link></td>
          </tr>
        </template>
      </v-data-table>
  </div>
</template>

<script>

export default {
  name: 'StudentList',
  props: {
    students: Array
  },
  data: () => ({
    expand: false,
    headers: [
      { text: 'First name', align: 'left', value: 'firstname', width: 20 },
      { text: 'Last Name', align: 'left', value: 'lastname', width: 20 },
      { text: 'Email', align: 'left', value: 'email', width: 30 },
      { text: 'Report card', align: 'right', value: '', width: 30 }
    ],
    students: []
  }),
  methods: {}
}
</script>

<style>

</style>
