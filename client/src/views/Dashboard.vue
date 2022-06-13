<template>
  <div class="mx-auto">
    <v-container fluid>
      <v-layout fill-height column>
        <div class="d-flex flex-column">
          <div class="d-flex justify-space-between">
              <div style="width: 600px;">
                <material-chart-card
                  type="Bar"
                  color="grey"
                  offset="0"
                  :data="chartData"
                  :options="chartOptions">
                  <v-overlay opacity="0.8" absolute="true" value="true">
                    <h4> Charts coming soon!</h4>
                  </v-overlay>
                </material-chart-card>
              </div>
              <activity-list />
          </div>
        </div>
      </v-layout>
    </v-container>
  </div>
</template>

<script>
import ActivityList from '../components/ActivityList.vue'
import MaterialChartCard from '../components/ChartCard.vue'

export default {
  name: 'Dashboard',
  components: {
    ActivityList,
    MaterialChartCard
  },
  methods: {},
  data () {
    return {
      chartData: {
        labels: ['Anna', 'Bridget', 'Chris'],
        series: [
          [49, 62, 64]
        ]
      },
      chartOptions: {}
    }
  }
}
</script>

<style scoped>
.div-dashboard {
  margin: 0;
  padding: 0;
}
</style>
