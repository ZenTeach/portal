<template>
  <div class="mx-auto">
    <v-container fluid>
      <v-layout fill-height row column>
        <v-flex xs12 sm12 md4 lg6 class="d-flex order-2 justify-space-between">
          <div style="width: 500px;"></div>
          <activity-list />
        </v-flex>
      </v-layout>
    </v-container>
  </div>
</template>

<script>
import ActivityList from '../components/ActivityList.vue'

export default {
  name: 'Dashboard',
  components: {
    ActivityList
  },
  methods: {},
  data () {
    return {}
  }
}
</script>

<style scoped>
.div-dashboard {
  margin: 0;
  padding: 0;
}
</style>
