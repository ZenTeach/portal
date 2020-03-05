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
      { text: 'First name', align: 'left', value: 'firstname', width: 30 },
      { text: 'Last Name', align: 'left', value: 'lastname', width: 30 },
      { text: 'Email', align: 'left', value: 'email', width: 40 }
    ],
    students: []
  }),
  methods: {}
}
</script>

<style>

</style>
