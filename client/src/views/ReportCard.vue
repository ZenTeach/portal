<template>
 <v-container>
  <v-layout column wrap justify-space-between>
    <div class="d-flex flex-column">
      <span v-if="has_reportcard">
        <h2 class="">Report Card</h2>
        <p>Total score: {{ total_score }}</p>
      </span>
    </div>
    <report-card-component :reports="reports || []" />
  </v-layout>
 </v-container>
</template>

<script>
import ReportCardComponent from '@/components/ReportCardComponent'
import { createNamespacedHelpers } from 'vuex'

const { mapGetters } = createNamespacedHelpers('quiz')
export default {
  name: 'ReportCard',
  components: {
    ReportCardComponent
  },
  computed: {
    ...mapGetters({ reports: 'reportCard' }),
    uniqueId () {
      return this.$route.params.uuid
    },
    has_reportcard: function () {
      return !this._.isEmpty(this._.omitBy(this.reports, this._.isNil))
    }
  },
  mounted: function () {
    this.$store.dispatch('quiz/FETCH_REPORTCARD', this.uniqueId, { root: true })
      .then((attainedScore) => {
        this.total_score = attainedScore
      })
  },
  data: () => {
    return {
      total_score: ''
    }
  }
}
</script>

<style scoped>
table, caption, tbody, tfoot, thead, tr, th, td {
  margin: 0;
  padding: 0;
  border: 0;
  font-size: 100%;
  font: inherit;
  vertical-align: baseline;
}
table  {
  border-collapse:collapse;
  border-spacing:0;
}
table td {
  font-family:Arial, sans-serif;
  font-size:14px;
  padding:10px 5px;
  border-style:solid;
  border-width:1px;
  overflow:hidden;
  word-break:normal;
  border-color:black;
}

table th {
  font-family:Arial, sans-serif;
  font-size:14px;
  font-weight:normal;
  padding:10px 5px;
  border-style:solid;
  border-width:1px;
  overflow:hidden;
  word-break:normal;
  border-color:black;
}
.tg .tg-cly1{text-align:left;vertical-align:middle}
</style>
