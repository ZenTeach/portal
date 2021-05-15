<template>
    <ValidationObserver ref="edit_observer">
        <question-form
            :question_object="editableQuestion"
            :knowledge_items="knowledge_items"
            :topics="topics"
            :subjects="subjects"
            :exam_board="exam_board"
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
import {
  ValidationObserver
} from 'vee-validate'

const {
  mapGetters: questionsGetters,
  mapMutations: questionsMutations,
  mapActions: questionsActions
} = createNamespacedHelpers('questions')
const { mapActions: appActions, mapGetters: appGetters } = createNamespacedHelpers('app')

export default {
  name: 'QuestionEdit',
  components: {
    QuestionForm,
    ValidationObserver
  },
  computed: {
    ...questionsGetters({
      currentQuestion: 'CURRENTQUESTION'
    }),
    ...appGetters({
      getSubjects: 'getSubjects',
      getKis: 'getKis',
      topics: 'getTopics'
    })
  },
  beforeMount: function () {
    const enabledSubjects = this._.filter(this.getSubjects, ['enabled', true])
    this.subjects = this._.map(enabledSubjects, 'name')

    const { id, ...editableQuestion } = Object.assign({}, this.currentQuestion)
    editableQuestion.question_type = 'multiple_choice'
    editableQuestion.subject = editableQuestion.subject.name
    this.editableQuestion = editableQuestion
  },
  data: function () {
    return {
      subjects: [],
      exam_board: [
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
      editableQuestion: {}
    }
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
    // renameWith(obj, keyMapping) {
    //     function rename(obj, key, newKey) {
    //             if(this._.includes(this._.keys(obj), key)) {
    //                 obj[newKey] = this._.clone(obj[key], true);

    //                 delete obj[key];
    //             }

    //             return obj;
    //     }

    //     let objMapper = this._.partial(rename)(obj)
    //     let r
    //     for (const values of keyMapping) {
    //         r = objMapper(values)
    //     }
    //     return r
    // },
    triggerTopicFetch () {
      this.fetchTopics(this.editableQuestion.subject)
    },
    triggerKIFetch () {
      const payload = {
        topics_selected: [this.editableQuestion.topic]
      }
      this.fetchKis(payload)
    },
    cleanupAndExit () {
      this.unsetCurrentQuestion()
      this.$router.back()
    },
    validate () {
      if (this.$refs.create_observer.validate()) {
        return true
      }
      return false
    },
    processSubmit () {
      if (this.validate) {
        console.log(this.editableQuestion)
        const payload = Object.assign({}, this.editableQuestion)
        this.updateQuestion({
          questionId: this.currentQuestion.id,
          payload: payload
        })
      }
    }
  }
}
</script>
