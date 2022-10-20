<template>
    <ValidationObserver ref="_observer">
        <question-form
            ref="question_form"
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
const { mapGetters: userGetters } = createNamespacedHelpers('user')

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
    }),
    ...userGetters({
      currentUser: 'getCurrentUser'
    })
  },
  beforeMount: function () {
    this.questionObject = this.processCurrentQuestion(this.currentQuestion)
    this.suggestedExamBoardsForSubjects(this.questionObject.subject)
    this.exam_boards = this.default_exam_board
    this.fetchTopics(this.questionObject.subject)
    if (this.questionObject.topic && this.questionObject.topic.value) {
      this.triggerKIFetch()
    }
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
        const _payload = Object.assign({}, this.questionObject)
        const { isActive, ...payload } = _payload
        if (this.retryingRequest === false) {
          this.convertToQuillDelta(payload.choices)
        }
        payload.topic = payload.topic.value || payload.topic
        payload.knowledge_item = payload.knowledge_item.value || payload.knowledge_item
        payload.teacher_id = payload.teacher_id || this.currentUser.id
        this.updateQuestion({
          questionId: this.currentQuestion.id,
          payload: payload
        }).catch(function (exception) {
          this.retryingRequest = true
        })
        this.retryingRequest = !this.retryingRequest
      }
    }
  }
}
</script>
