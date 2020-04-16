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
      <template v-for="knowledge_item, idx in report.knowledge_items">
        <tr :key="knowledge_item">
          <td class="tg-cly1" :class="tg-cly1" :rowspan="report.knowledge_items.length" v-if="idx === 0">{{ report.topic }}</td>
          <td class="tg-0lax">{{ knowledge_item}}</td>
          <td class="tg-0lax">{{ report.progress[idx] }}</td>
          <td class="tg-0lax">{{ report.resources[idx]}}</td>
        </tr>
      </template>
    </template>
  </tbody>
  </template>
   </v-simple-table>
  </v-layout>
 </v-container>
</template>

<script>
export default {
  name: 'ReportCard',
  data: () => {
    return {
      reports: [{
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
        resources: [
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
        resources: [
          'This video explains electron shells quite nicely.',
          'Revise theses lesson slides.',
          'This video explains electron shells quite nicely.'
        ]
      }]
    }
  }
}
</script>

<style scoped>
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
