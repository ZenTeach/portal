<template>
  <ValidationObserver ref="edit_observer" v-slot="{ invalid, validated, handleSubmit }">
    <material-card title="" :elevation="23" class="grey lighten-3">
      <v-card-text >
        <v-container>
          <v-row>
              <v-col cols="10" lg="12" sm="12" md="12" class="flex">
                  <ValidationProvider rules="required" name="question" v-slot="{ errors }">
                  <v-text-field label="Question"
                    v-model="create_question.question"
                    :error-messages="errors"
                    color="" outlined grow></v-text-field>
                  </ValidationProvider>
              </v-col>
          </v-row>
          <v-row>
              <v-col cols="3" lg="3" sm="12" md="6">
                  <ValidationProvider rules="required" name="subject" v-slot="{ errors }">
                      <v-select
                          :items="subjects"
                          label="Subject"
                          @change="triggerTopicFetch()"
                          :error-messages="errors"
                          v-model="create_question.subject"
                          outlined></v-select>
                  </ValidationProvider>
              </v-col>
              <v-col cols="3" lg="3" sm="12" md="6">
                  <ValidationProvider rules="required" name="topic" v-slot="{ errors }">
                  <v-select
                      :items="getTopics"
                      label="Topic"
                      :error-messages="errors"
                      @change="triggerKIFetch()"
                      v-model="create_question.topic"
                      outlined></v-select>
                  </ValidationProvider>
              </v-col>
              <v-col cols="3" lg="3" sm="12" md="6">
                  <ValidationProvider rules="required" name="knowledge_item" v-slot="{ errors }">
                      <v-select
                          :items="knowledge_items"
                          :error-messages="errors"
                          label="Knowledge Item"
                          v-model="create_question.knowledge_item"
                          outlined></v-select>
                  </ValidationProvider>
              </v-col>
              <v-col cols="3" lg="3" sm="12" md="6">
                  <ValidationProvider name="question_type" rules="required" v-slot="{ errors }">
                  <v-select :items="question_type"
                      :error-messages="errors"
                      value="multiple_choice"
                      placeholder="Multiple Choice"
                      :disabled="true"
                      v-model="create_question.question_type" label="Question Type" outlined
                  ></v-select>
                  </ValidationProvider>
              </v-col>
              <v-col cols="12" lg="12" sm="12" md="12">
                  <ValidationProvider name="tag" rules="required" v-slot="{ errors }">
                  <v-text-field
                      v-model="create_question.tag"
                      label="Tag"
                      single-line
                      :error-messages="errors"
                      outlined
                  ></v-text-field>
                  </ValidationProvider>
              </v-col>
          </v-row>
          <v-row>
            <span class="inline-flex">
              <v-row>
                <v-col>
                  <h2 class="my-3">Choices</h2>
                  <!-- <v-btn color="success" class="my-3" @click="addChoiceEditor">Add</v-btn> -->
                </v-col>
              </v-row>
            </span>
            <hr class="my-3"/>
              <v-col cols="12">
                  <questions-choices :choice="create_question.choices[0]" :disable_validation="validate_multiple_choices"/>
              </v-col>
              <v-col cols="12">
                  <questions-choices :choice="create_question.choices[1]" :disable_validation="validate_multiple_choices"/>
              </v-col>
              <v-col cols="12">
                  <questions-choices :choice="create_question.choices[2]" :disable_validation="validate_multiple_choices"/>
              </v-col>
              <v-col cols="12">
                  <questions-choices :choice="create_question.choices[3]" :disable_validation="validate_multiple_choices"/>
              </v-col>
          </v-row>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <div class="flex-grow-1"></div>
        <v-btn color="green darken-1" @click="processSubmit" outlined >Create Question</v-btn>
        <v-btn color="red darken-1" @click="$router.back()" outlined>Cancel and Go back</v-btn>
      </v-card-actions>
    </material-card>
  </ValidationObserver>
</template>
<script>
import MaterialCard from '@/components/MaterialCard'
import QuestionsChoices from '@/components/QuestionsChoices'
import { createNamespacedHelpers } from 'vuex'
import {
  ValidationObserver,
  ValidationProvider
} from 'vee-validate'

const { mapActions, mapGetters } = createNamespacedHelpers('app')
const { mapActions: questionActions } = createNamespacedHelpers('questions')

export default {
  name: 'QuestionCreate',
  components: {
    MaterialCard,
    ValidationObserver,
    ValidationProvider,
    QuestionsChoices
  },

  computed: {
    ...mapGetters({
      getSubjects: 'getSubjects',
      getKis: 'getKis',
      getTopics: 'getTopics'
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
      if (this.$refs.edit_observer.validate()) {
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
