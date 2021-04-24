<template>
  <v-container fluid>
    <v-flex xs12 sm12 md12 lg12>
      <v-row>
        <v-col>
          <material-card title="Question Lists">
            <div>
              <question-search-result
                :resultSet='this.questionList'
                :selectable='false'
                :show_user_created_badge='false'
              />
            </div>
          </material-card>
        </v-col>
      </v-row>
    </v-flex>
  </v-container>
</template>
<script>

import MaterialCard from '@/components/MaterialCard'
import QuestionSearchResult from '@/components/QuestionSearchResult'
import { createNamespacedHelpers } from 'vuex'

const { mapActions, mapGetters } = createNamespacedHelpers('questions')

export default {
  name: 'Questions',
  components: {
    MaterialCard,
    QuestionSearchResult
  },
  mounted: function () {
    this.fetchQuestions()
  },
  computed: {
    ...mapGetters({
      questionList: 'QUESTIONLIST'
    })
  },
  methods: {
    ...mapActions({
      fetchQuestions: 'GETQUESTIONS'
    })
  }
}
</script>
