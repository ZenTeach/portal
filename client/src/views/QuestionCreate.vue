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
        <v-btn color="green darken-1" @click="processSubmit" outlined >Create Question</v-btn>
        <v-btn color="red darken-1" @click="$router.back()" outlined>Cancel and Go back</v-btn>
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

const { mapActions, mapGetters } = createNamespacedHelpers('app')
const {
  mapActions: questionActions,
  mapGetters: questionsGetters,
  mapMutations: questionsMutations
} = createNamespacedHelpers('questions')
const { mapGetters: classRoomGetters } = createNamespacedHelpers('classrooms')

export default {
  name: 'QuestionCreate',
  components: {
    ValidationObserver,
    QuestionForm
  },
  mixins: [QuestionCRUDMixin],
  computed: {
    ...questionsGetters({
      currentQuestion: 'CURRENTQUESTION'
    }),
    ...questionsMutations({
      unsetCurrentQuestion: 'UNSET_CURRENTQUESTION'
    }),
    ...mapGetters({
      getSubjects: 'getSubjects',
      getKis: 'getKis',
      topics: 'getTopics'
    }),
    ...classRoomGetters({
      classList: 'CLASSLIST'
    })
  },

  beforeMount: function () {
    if (this.currentQuestion) {
      this._.merge(this.questionObject, this.processCurrentQuestion(this.currentQuestion))
      console.log(this.questionObject, this.processCurrentQuestion(this.currentQuestion))
      this.triggerKIFetch()
    }
  },

  data: function () {
    // merge default data
    const questionObject = {
      subject: '',
      exam_board: '',
      topic: '',
      knowledge_item: '',
      tag: '',
      question_type: 'multiple_choice',
      question: '',
      choices: [
        { value: '', weight: 0, is_correct_choice: false, feedback: '' },
        { value: '', weight: 0, is_correct_choice: false, feedback: '' },
        { value: '', weight: 0, is_correct_choice: false, feedback: '' },
        { value: '', weight: 0, is_correct_choice: false, feedback: '' }
      ]
    }

    return Object.assign(
      {
        questionObject: questionObject
      },
      this.initData()
    )
  },
  methods: {
    ...mapActions({
      fetchKis: 'FETCH_KIS',
      fetchTopics: 'FETCH_TOPICS'
    }),
    ...questionActions({
      postQuestion: 'CREATEQUESTION'
    }),
    processSubmit () {
      if (this.validate) {
        this.postQuestion(this.questionObject)
      }
      if (this.currentQuestion) {
        this.unsetCurrentQuestion()
      }
    }
  }
}
</script>
<style scoped>
</style>
