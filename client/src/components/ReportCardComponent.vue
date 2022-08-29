<template>
  <v-layout>
   <v-simple-table v-if="has_reportcard">
    <template v-slot:default>
     <thead>
        <tr>
          <th class="text-left">Topic</th>
          <th class="text-left">Knowledge items</th>
          <th class="text-left">Progress</th>
          <th class="text-left">Feedback / Learning resources</th>
        </tr>
     </thead>
     <tbody>
       <template v-if="reports.length === 0">
         <tr>
           <td :colspan="4">
             <h3 class="text-center"> Report card has not been processed yet! </h3>
           </td>
         </tr>
       </template>
       <template v-for="report in reports" v-else>
         <template v-for="(topic,) in Object.keys(report)">
          <tr :key="topic" colspan="1">
           <td class="tg-cly1" :rowspan="Object.keys(report[topic]).length + 1" colspan="1">{{ topic }}</td>
          </tr>
          <tr v-for="(knowledge_item, idx) in Object.keys(report[topic])" :key="knowledge_item + idx">
            <td class="tg-0lax" :key="idx">{{ knowledge_item }}</td>
            <td :class="highlightProgress(report[topic][knowledge_item].progress)" :key="knowledge_item + idx + 'progress'">{{ report[topic][knowledge_item].progress }}</td>
            <td class="tg-0lax" v-html="convertDeltaToHTML(report[topic][knowledge_item].feedback)" :key="knowledge_item + idx + 'feedback'">{{}}</td>
          </tr>
         </template>
       </template>
     </tbody>
   </template>
  </v-simple-table>
   <div v-else>
     <v-card min-width="60vw" class="d-flex flex-column my-5 justify-center">
       <v-card-title class="p-8">
         <h3>Report card is being graded!</h3>
       </v-card-title>
       <v-card-text>
       We're working on grading your report card. Please come back at a later time to check your results.
        </v-card-text>
     </v-card>
   </div>
   </v-layout>
</template>

<script>
import { QuillDeltaToHtmlConverter } from 'quill-delta-to-html'

export default {
  name: 'ReportCardComponent',
  props: {
    reports: {
      type: Array,
      default: [],
      required: true
    }
  },
  data: () => {
    return {
    }
  },
  computed: {
    has_reportcard: function () {
      return !this._.isEmpty(this._.omitBy(this.reports, this._.isNil))
    }
  },
  methods: {
    highlightProgress (progress) {
      if (progress === '') return
      const [nom, denom] = progress.split('/').map(element => parseInt(element))
      // const [nom, ...denom] = parsed

      if (nom === denom) {
        return 'green'
      } else if (nom === 0) {
        return 'red lighten-2'
      } else {
        return 'yellow darken-2'
      }
    },
    convertDeltaToHTML (feedback) {
      if (feedback.length === 0) {
        return 'No feedback provided.'
      }
      try {
        const deltaOps = JSON.parse(feedback)
        const cfg = {}
        const converter = new QuillDeltaToHtmlConverter(deltaOps, cfg)
        let converted_ = converter.convert()
        if (converted_ instanceof Array) {
          converted_ = converted_.join('\n')
        }
        return converted_
      } catch (error) {
        if (feedback instanceof Array) {
          return feedback.join('\n')
        }
        return feedback
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
table thead, table thead > th {
  padding: 2px;
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
  border-width:0px;
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
  border-width:0px;
  overflow:hidden;
  word-break:normal;
  border-color:black;
}
.tg .tg-cly1{text-align:left;vertical-align:middle}
</style>
