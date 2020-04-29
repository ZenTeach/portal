<template>
 <v-container>
  <v-layout row column wrap justify-center>
   <v-simple-table>
    <template v-slot:default>
     <thead>
      <tr>
        <th class="text-left">Topic</th>
          <th class="text-left">Knowledge items</th>
          <th class="text-left">Progress</th>
          <th class="text-left">Learning resources</th>
        </tr>
     </thead>
  <tbody>
    <template v-for="report in reports">
        <tr v-for="(knowledge_item, idx) in report.knowledge_item" :key="knowledge_item">
          <td class="tg-cly1" :rowspan="report.knowledge_item.length" v-if="idx === 0">{{ report.topic }}</td>
          <td class="tg-0lax">{{ knowledge_item}}</td>
          <td :class="highlightProgress(report.progress[idx])">{{ report.progress[idx] }}</td>
          <td class="tg-0lax">{{ report.feedback[idx]}}</td>
        </tr>
    </template>
  </tbody>
  </template>
   </v-simple-table>
  </v-layout>
 </v-container>
</template>

<script>
import { createNamespacedHelpers } from 'vuex'
const { mapGetters } = createNamespacedHelpers('quiz')
export default {
  name: 'ReportCard',
  computed: {
    ...mapGetters({ reports: 'reportCard' }),
    uniqueId () {
      return this.$route.params.uuid
    }
  },
  mounted: async function () {
    await this.$store.dispatch('quiz/FETCH_REPORTCARD', this.uniqueId, { root: true })
  },
  data: () => {
    return {
      reportsx: [{
        topic: 'Atoms and elements',
        knowledge_items: [
          'Atoms are made up of protons, neutrons and electrons',
          'Electrons circle the nucleus.',
          'Protons and neutrons are located inside the nucleus.',
          'Protons and neutrons have a mass of 1.',
          'Electrons have a mass of 0.'
        ],
        progress: [
          '1/2',
          '0/1',
          '0/1',
          '1/1',
          '1/1'
        ],
        feedback: [
          'Look at this image of an atom.',
          'Look at this image of an atom.',
          'Look at this image of an atom.',
          'Look at this image of an atom.',
          'Look at this image of an atom.'
        ]
      },
      {
        topic: 'Charges and Ions',
        knowledge_items: [
          'Two electrons or two protons repel each other.',
          'Atoms have a neutral charge.',
          'All atoms want to achieve a full outer shell (usually 8 electrons)'
        ],
        progress: [
          '1/1',
          '0/1',
          '0/1'
        ],
        feedback: [
          'This video explains electron shells quite nicely.',
          'Revise theses lesson slides.',
          'This video explains electron shells quite nicely.'
        ]
      }]
    }
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
