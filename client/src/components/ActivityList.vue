<template>
  <div class="d-flex flex-column grey lighten-2">
    <div class="rounded-0 p-5">
      <p class="text-h6 text-left font-weight-bold">
            <v-icon class="mx-auto">
              mdi-format-list-bulleted-triangle
            </v-icon>
            Recent Activity
          </p>
    </div>
    <v-responsive
      v-if="has_logs"
      class="overflow-y-auto rounded-0"
      :max-height.sync="listHeight"
    >
      <v-list outlined dense disabled>
        <v-list-item-group color="primary border-1">
          <v-list-item v-for="log in logs" :key="log.action + '_' + log.item_type + '_' + log.item_id" two-line>
            <v-list-item-content>
              <v-list-item-title>
                <v-list-item-icon class="mx-auto">
                  <v-icon small>
                    {{ log.action }}
                  </v-icon>
                </v-list-item-icon>
                  <p class="d-inline-flex text-body-1 font-weight-normal activity-list-truncate"> {{ log.note }}</p>
              </v-list-item-title>
              <v-list-item-subtitle>
                  <p class="d-inline-flex text-caption text--disabled font-weight-light">
                    {{getRelativeDuration(log.created)}}
                  </p>
              </v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </v-list-item-group>
      </v-list>
    </v-responsive>
    <div v-else class="p-5 grey" style="width: 500px;">
      <span class="d-flex justify-center align-center">
        <v-icon class="mx-2" medium>cloud</v-icon>
        <p class="text-h5 mb-0 font-weight-light">No recent activity!</p>
      </span>
    </div>
    <div class="grey lighten-2 py-3 rounded">
      <p class="text-body-2 text--disabled text-center font-weight-black">
        Showing {{ logs.length }} items
      </p>
    </div>
  </div>
</template>

<script>
import moment from 'moment'
import { createNamespacedHelpers } from 'vuex'
const { mapActions } = createNamespacedHelpers('app')

export default {
  name: 'ActivityList',
  computed: {
    listHeight: function () {
      return (this.itemHeight * this.rowsPerPage) + 50
    },
    rowsPerPage () {
      return this.rpp
    },
    itemHeight () {
      switch (this.$vuetify.breakpoint.name) {
        case 'xs': return 50
        case 'sm': return 50
        case 'md': return 75
        case 'lg': return 100
        case 'xl': return 150
      }
    },
    has_logs () {
      return this.logs.length > 0
    }
  },
  data: function () {
    return {
      logs: [],
      rpp: 3
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
.activity-list-truncate {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
