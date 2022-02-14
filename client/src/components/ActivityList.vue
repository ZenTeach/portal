<template>
  <div class="w-1/2">
    <div>
      <v-list flat subheader tile>
        <v-subheader>
          <p class="text-h6 font-weight-bold">
            <v-icon class="mx-auto">
              mdi-format-list-bulleted-triangle
            </v-icon>
            Recent Activity
          </p>
        </v-subheader>
        <v-list-item-group color="primary">
          <v-list-item v-for="log in logs" :key="log.action + '_' + log.item_type + '_' + log.item_id">
            <v-list-item-icon>
              <v-icon small>
                {{ log.action }}
              </v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>
                  <p class="d-inline"> {{ log.note }}</p>
                  <p class="d-inline text-caption font-weight-black">
                    {{getRelativeDuration(log.created)}}
                  </p>
              </v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list-item-group>
      </v-list>
    </div>
  </div>
</template>

<script>
import moment from 'moment'
import { createNamespacedHelpers } from 'vuex'
const { mapActions } = createNamespacedHelpers('app')

export default {
  name: 'ActivityList',
  data: function () {
    return {
      logs: []
    }
  },
  mounted: function () {
    this.populateLogs()
  },
  methods: {
    ...mapActions({
      fetch_activities: 'FETCH_ACTIVITIES'
    }),
    async populateLogs () {
      this.logs = []
      this.logs = await this.fetch_activities()
    },
    getRelativeDuration (time) {
      return moment(time).fromNow()
    }
  }
}
</script>

<style>

</style>
