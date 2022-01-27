<template>
    <material-card title="" :elevation="23" class="grey lighten-3">
      <v-card-text >
        <v-container>
          <v-row>
              <v-col cols="10" lg="12" sm="12" md="12" class="flex">
                  <ValidationProvider rules="required" name="question" v-slot="{ errors }">
                  <v-text-field label="Question"
                    :placeholder="question_object.question || ''"
                    v-model="question_object.question"
                    :error-messages="errors"
                    color="" outlined grow></v-text-field>
                  </ValidationProvider>
              </v-col>
          </v-row>
          <v-row>
              <v-col cols="2" lg="2" sm="8" md="3">
                  <ValidationProvider mode="eager" rules="required" name="subjects" v-slot="{ errors }">
                      <v-select
                          :items="subjects"
                          label="Subject"
                          @change="subjectChangeHandler()"
                          :placeholder="question_object.subject || ''"
                          :error-messages="errors"
                          v-model="question_object.subject"
                          outlined></v-select>
                  </ValidationProvider>
              </v-col>
              <v-col cols="4" lg="4" sm="12" md="4">
                  <ValidationProvider mode="passive" rules="required" name="topic" v-slot="{ errors }">
                      <topic-select-with-ajax
                        :items="topics"
                        :subject="question_object.subject"
                        label="Topic"
                        :placeholder="question_object.topic.value || ''"
                        :error-messages="errors"
                        v-model="question_object.topic"
                        outlined
                      ></topic-select-with-ajax>
                  </ValidationProvider>
              </v-col>
              <v-col cols="4" lg="4" sm="12" md="4">
                  <ValidationProvider mode="passive" rules="required" name="knowledge_item" v-slot="{ errors }">
                      <ki-select-with-ajax
                          :items="knowledge_items"
                          :error-messages="errors"
                          label="Knowledge Item"
                          :placeholder="question_object.knowledge_item.value || ''"
                          :selectedTopic="question_object.topic.value"
                          :subject="question_object.subject"
                          v-model="question_object.knowledge_item"
                          outlined
                      >
                      </ki-select-with-ajax>
                  </ValidationProvider>
              </v-col>
          </v-row>
          <v-row>
              <v-col cols="3" lg="3" sm="12" md="6">
                  <ValidationProvider rules="required" name="exam_board" v-slot="{ errors }">
                      <SelectsWithSuggestion
                        :items="exam_board"
                        v-model="question_object.exam_board"
                        label="Exam Board"
                        :error-messages="errors"
                        :placeholder="translateExamBoard(question_object.exam_board)"
                        outlined/>
                  </ValidationProvider>

              </v-col>
          </v-row>
          <v-row>
            <span class="inline-flex">
              <v-row>
                <v-col>
                  <h2 class="my-3">Choices</h2>
                </v-col>
              </v-row>
            </span>
            <hr class="my-3"/>
              <v-col cols="12">
                  <questions-choices
                    v-for="(choice, idx) in question_object.choices"
                    :choice="question_object.choices[idx]"
                    :ref="'choiceEditor-' + idx"
                    :key="idx"
                    :disable_validation="validate_multiple_choices"/>
              </v-col>
              <!-- If no choices are given -->
              <template></template>
          </v-row>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <slot name="form_actions"></slot>
      </v-card-actions>
    </material-card>
</template>

<script>

import { ValidationProvider } from 'vee-validate'
import QuestionsChoices from './QuestionsChoices'
import MaterialCard from './MaterialCard'
import SelectsWithSuggestion from './SelectsWithSuggestion'
import TopicSelectWithAjax from './TopicSelectWithAjax'
import searchForKIListener from './KISelectWithAjax'
import KiSelectWithAjax from './KISelectWithAjax.vue'

export default {
  name: 'QuestionForm',
  components: {
    ValidationProvider,
    SelectsWithSuggestion,
    QuestionsChoices,
    MaterialCard,
    TopicSelectWithAjax,
    searchForKIListener,
    KiSelectWithAjax
  },
  props: {
    question_object: {
      type: Object
    },
    knowledge_items: {
      type: Array
    },
    topics: {
      type: Array
    },
    subjects: {
      type: Array
    },
    exam_board: {
      type: Array
    },
    question_type: {
      type: Array
    },
    topicChangeHandler: {
      type: Function
    },
    KIChangeHandler: {
      type: Function
    },
    subjectChangeHandler: {
      type: Function
    },
    validate_multiple_choices: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    translateExamBoard: function (value) {
      if (!value) return ''
      const it = this._.findIndex(this.exam_board, ['value', value])
      return this.exam_board[it].text
    }

  }
}
</script>
