<template>
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
       <template v-if="reports.length === 0">
         <tr>
           <td :colspan="4">
             <h3 class="text-center"> Report card not processed yet! </h3>
           </td>
         </tr>
       </template>
       <template v-for="report in reports" v-else>
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
</template>

<script>
export default {
  name: 'ReportCardComponent',
  props: {
    reports: {
      type: Array,
      required: true
    }
  },
  data: () => {
    return {
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
