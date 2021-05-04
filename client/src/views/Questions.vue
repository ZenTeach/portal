<template>
  <v-container fluid>
    <v-flex xs12 sm12 md12 lg12>
      <v-row>
        <v-col>
          <router-link to="/question/create" >
            <v-btn color="primary" class="float-right mx-4" dark>Create a question</v-btn>
          </router-link>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <material-card>
            <template v-slot:header>
              <div class="px-3 d-flex align-center">
                <h4 class="title font-weight-light mb-2">Question Lists</h4>
                <v-spacer></v-spacer>

              </div>
            </template>
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
const { mapActions: appActions, mapGetters: appGetters } = createNamespacedHelpers('app')

export default {
  name: 'Questions',
  components: {
    MaterialCard,
    QuestionSearchResult
  },
  mounted: function () {
    this.fetchQuestions()
  },
  data: function () {
    return {}
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
