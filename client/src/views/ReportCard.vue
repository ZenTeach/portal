<template>
 <v-container>
  <v-layout row column wrap justify-center>
    <report-card-component v-bind:reports="reports" />
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
    }
  },
  mounted: function () {
    this.$store.dispatch('quiz/FETCH_REPORTCARD', this.uniqueId, { root: true })
  },
  data: () => {
    return {}
  },
  methods: {
    highlightProgress (progress) {
      const parsed = progress.split('/').map(element => parseInt(element))
      const [nom, ...denom] = parsed

      if (nom === denom) {
        return 'green'
      } else if (nom === 0) {
        return 'red'
      } else {
        return 'yellow'
      }
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
