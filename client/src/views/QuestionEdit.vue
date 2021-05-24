<template>
    <ValidationObserver ref="_observer">
        <question-form
            :question_object="questionObject"
            :knowledge_items="knowledge_items"
            :topics="topics"
            :subjects="subjects"
            :exam_board="exam_boards"
            :question_type="question_type"
            :topicChangeHandler="triggerTopicFetch"
            :KIChangeHandler="triggerKIFetch"
        >
            <template v-slot:form_actions>
                <div class="flex-grow-1"></div>
                <v-btn color="green darken-1" @click="processSubmit" outlined >Edit Question</v-btn>
                <v-btn color="red darken-1" @click="cleanupAndExit()" outlined>Cancel and Go back</v-btn>
            </template>
        </question-form>
    </ValidationObserver>
</template>

<script>

import QuestionForm from '@/components/QuestionForm'
import { createNamespacedHelpers } from 'vuex'
import { QuestionCRUDMixin } from '@/mixins/QuestionCRUDMixin'
import {
  ValidationObserver
} from 'vee-validate'

const {
  mapGetters: questionsGetters,
  mapMutations: questionsMutations,
  mapActions: questionsActions
} = createNamespacedHelpers('questions')

const { mapActions: appActions, mapGetters: appGetters } = createNamespacedHelpers('app')
const { mapGetters: classRoomGetters } = createNamespacedHelpers('classrooms')

export default {
  name: 'QuestionEdit',
  components: {
    QuestionForm,
    ValidationObserver
  },
  mixins: [QuestionCRUDMixin],
  computed: {
    ...questionsGetters({
      currentQuestion: 'CURRENTQUESTION'
    }),
    ...appGetters({
      getSubjects: 'getSubjects',
      getKis: 'getKis',
      topics: 'getTopics'
    }),
    ...classRoomGetters({
      classList: 'CLASSLIST'
    })
  },
  beforeMount: function () {
    const { id, ...questionObject } = Object.assign({}, this.currentQuestion)
    questionObject.question_type = 'multiple_choice'
    questionObject.subject = this._.get(questionObject, 'subject.name', '')
    this.questionObject = questionObject
  },
  data: function () {
    return this.initData()
  },
  methods: {
    ...appActions({
      fetchKis: 'FETCH_KIS',
      fetchTopics: 'FETCH_TOPICS'
    }),
    ...questionsActions({
      updateQuestion: 'UPDATEQUESTION'
    }),
    ...questionsMutations({
      unsetCurrentQuestion: 'UNSET_CURRENTQUESTION'
    }),
    cleanupAndExit () {
      this.unsetCurrentQuestion()
      this.$router.back()
    },
    processSubmit () {
      if (this.validate) {
        const payload = Object.assign({}, this.questionObject)
        this.updateQuestion({
          questionId: this.currentQuestion.id,
          payload: payload
        })
      }
    }
  }
}
</script>
