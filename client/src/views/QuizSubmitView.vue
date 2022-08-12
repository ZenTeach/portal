<template>
  <v-container fluid>
    <v-layout v-if="!this.private_">
      <v-card max-width="800" width="800" class="mx-12 rounded-1 p-3">
        <v-card-title> You've submitted!</v-card-title>
        <v-card-subtitle>
          <small>Please wait while we grade your answers to {{quizName}}</small>
          </v-card-subtitle>
          <v-card-text>
            <p>Please save this link to check your results later.</p>
            <code>https://portal.zenteach.co.uk/</code>
          </v-card-text>
        </v-card>
      </v-layout>
  </v-container>
</template>

<script>
import { createNamespacedHelpers } from 'vuex'

const { mapGetters, mapActions } = createNamespacedHelpers('quiz')
export default {
  name: 'QuizSubmitView',
  computed: {
    quiz_uuid: function () {
      return this.$route.params.uuid
    },
    ...mapGetters({
      quizName: 'name',
      private_: 'private_'
    })

  },
  mounted: function () {
    // load quiz info
    this.loadQuiz(this.quiz_uuid)
  },
  method: {
    ...mapActions({
      loadQuiz: 'LOAD_QUIZ'
    })
  }
}
</script>
