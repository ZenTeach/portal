<template>
  <ValidationObserver ref="create_observer">
    <question-form 
      :question_object="create_question"
      :knowledge_items="knowledge_items"
      :topics="topics"
      :subjects="subjects"
      :exam_boards="exam_boards"
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
import {
  ValidationObserver
} from 'vee-validate'

const { mapActions, mapGetters } = createNamespacedHelpers('app')
const { mapActions: questionActions } = createNamespacedHelpers('questions')

export default {
  name: 'QuestionCreate',
  components: {
    ValidationObserver,
    QuestionForm
  },

  computed: {
    ...mapGetters({
      getSubjects: 'getSubjects',
      getKis: 'getKis',
      topics: 'getTopics'
    })
  },
  mounted: function () {
    const enabledSubjects = this._.filter(this.getSubjects, ['enabled', true])
    this.subjects = this._.map(enabledSubjects, 'name')
  },
  watch: {
    getKis: function (val) {
      this.knowledge_items = []
      this.knowledge_items = this._.flatten(this._.values(this.getKis))
    },
    'create_question.question_type': function (val) {
      if (val === 'multiple_choice') {
        this.validate_multiple_choices = false
      }
    }
  },
  data: function () {
    return {
      create_question: {
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

      },
      subjects: [],
      exam_boards: [
        { value: 'aqa', text: 'AQA' },
        { value: 'ocr_gateway', text: 'OCR Gateway' },
        { value: 'edexcel', text: 'EdExcel' },
        { value: 'ocr_new', text: 'OCR 21st Century' },
        { value: 'wjec', text: 'WJEC' },
        { value: 'ccea', text: 'CCEA' },
        { value: 'eduqas', text: 'Eduqas' }
      ],
      question_type: [
        { text: 'Multiple Choice', value: 'multiple_choice' },
        { text: 'Short Answer', value: 'short_answer' },
        { text: 'Long Answer', value: 'long_answer' }
      ],
      knowledge_items: [],
      validate_multiple_choices: false
    }
  },
  methods: {
    ...mapActions({
      fetchKis: 'FETCH_KIS',
      fetchTopics: 'FETCH_TOPICS'
    }),
    ...questionActions({
      postQuestion: 'CREATEQUESTION'
    }),
    triggerTopicFetch () {
      this.fetchTopics(this.create_question.subject)
    },
    triggerKIFetch () {
      const payload = {
        topics_selected: [this.create_question.topic]
      }
      this.fetchKis(payload)
    },
    validate () {
      if (this.$refs.create_observer.validate()) {
        return true
      }
      return false
    },
    processSubmit () {
      if (this.validate) {
        this.postQuestion(this.create_question)
      }
    }
  }
}
</script>
<style scoped>
</style>
