<template>
  <v-stepper v-model="curator">
    <v-stepper-header>
      <v-stepper-step step="1" editable :complete="curator > 1">Topic selection</v-stepper-step>

      <v-divider></v-divider>

      <v-stepper-step step="2" editable :complete="curator > 2">Choose questions</v-stepper-step>

      <v-divider></v-divider>

      <v-stepper-step step="3" editable :complete="curator > 3">Finalize quiz</v-stepper-step>
    </v-stepper-header>

    <v-stepper-items>
      <v-stepper-content step="1">
        <v-card color="grey lighten-4" class="mx-auto">
          <v-card-title>Select topics and knowledge items</v-card-title>
          <v-card-text>
            <v-select
              :items="questionTopics"
              required
              multiple
              chips
              @change="fetch_KIs()"
              label="Topic: "
              v-model="topicsSelected"
              :rules="[() => topicsSelected.length > 0 || 'You must choose at least one']"
            ></v-select>

            <v-spacer class="ma-3 mb-3"></v-spacer>

            <v-select
              label="Knowledge Items: "
              multiple
              chips
              required
              :items="knowledgeItems"
              :rules="[() => selectedKnowledgeItems.length > 0 || 'You must choose at least one']"
              v-model="selectedKnowledgeItems"
            ></v-select>
          </v-card-text>
          <v-card-actions class="justify-space-between px-5">
            <div>
              <v-btn color="primary" class="mr-2" @click="curator = 2">Continue</v-btn>
              <v-btn color="success" @click="createQuizFastTracked()">Finish</v-btn>
            </div>
            <v-btn @click.native.prevent="closeDialog()" class="float-left error">Cancel</v-btn>
          </v-card-actions>
        </v-card>
      </v-stepper-content>
      <v-stepper-content step="2">
        <v-card color="grey lighten-4" class="mx-auto">
          <v-card-title>Search for Questions</v-card-title>
          <v-card-text>
            <question-search v-bind:subject="subject" v-bind:topics="topicsSelected" v-bind:knowledge_items="selectedKnowledgeItems" v-on:update:searchResult="populateSearchResult"/>
            <question-search-result v-bind:resultSet="questionSearch" v-show="hasSearchResult"/>
          </v-card-text>
          <v-card-actions class="justify-space-between px-5">
            <v-btn color="primary" @click="curator = 3">Continue</v-btn>
            <v-btn @click.native.prevent="closeDialog()" class="float-left error">Cancel</v-btn>
          </v-card-actions>
        </v-card>
      </v-stepper-content>
      <v-stepper-content step="3">
        <v-card color="grey lighten-4" class="mx-auto">
          <v-card-title>Finalize Quiz</v-card-title>
            <v-card-text>
              <h4 class="text-subtitle-1">Selected topics & knowledge items</h4>
              <v-list>
                <v-list-group v-for="topic in topicsSelected" :key="topic">
                    <v-icon :key="topic">
                      mdi-checkbox
                    </v-icon>
                    <template v-slot:activator>
                      <v-list-item-title>{{topic}}</v-list-item-title>
                    </template>
                    <!-- <p class="text-subtitle-1">Selected Knowledge Items:</p> -->
                    <v-list-item v-for="kis in selectedKnowledgeItems" :key="kis">
                      <v-list-item-title v-text="kis"></v-list-item-title>
                      <v-list-item-icon>
                        <v-icon>mdi-checkbox-marked-circle</v-icon>
                      </v-list-item-icon>
                    </v-list-item>
                </v-list-group>
              </v-list>
            </v-card-text>
            <v-card-actions class="justify-space-between px-5">
              <v-btn color="primary" @click="createQuiz()">Continue</v-btn>
              <v-btn @click.native.prevent="closeDialog()" class="float-left error">Cancel</v-btn>
            </v-card-actions>
          </v-card>
        </v-stepper-content>
      </v-stepper-items>
    </v-stepper>
</template>

<script>
import QuestionSearch from '@/components/QuestionSearch'
import QuestionSearchResult from '@/components/QuestionSearchResult'
import Api from '@/service/Api'

import { createNamespacedHelpers } from 'vuex'
const { mapState, mapActions } = createNamespacedHelpers('app')

export default {
  name: 'QuizCreator',
  components: {
    QuestionSearch,
    QuestionSearchResult
  },
  computed: {
    ...mapState({
      questionSearch: state => state.questionSearch,
      questionList: state => state.questionList,
      knowledgeItems: state => state.knowledgeItems,
      questionTopics: state => state.topics
    }),
    subject () {
      const classData = this.$store.getters['classrooms/CLASSLIST']
      const filtered = classData.find(x => {
        const classId = parseInt(this.$route.params.id)
        return x.id === classId
      })
      return filtered.subject
    }
  },
  mounted: function () {
    this.$store.dispatch('app/FETCH_TOPICS', this.subject, { root: true })
  },
  data () {
    return this.initial()
  },
  methods: {
    ...mapActions({
      fetchQuestionsFastTracked: 'FETCH_QUESTIONS_FASTTRACKED'
    }),
    initial () {
      return {
        curator: 1,
        questionSearchResult: [],
        hasSearchResult: false,
        topicsSelected: [],
        selectedKnowledgeItems: []
      }
    },
    createQuiz () {
      const payload = {
        subject: this.subject,
        class_id: this.$route.params.id,
        questions: this.questionList
      }
      Api.post(
        '/class_quiz',
        payload
      ).then(() => {
        this.closeDialog()
      })
    },
    createQuizFastTracked () {
      this.fetchQuestionsFastTracked(this.topicsSelected, this.selectedKnowledgeItems)
        .then(() => {
          this.hasSearchResult = true
          this.curator = 3
        })
    },
    closeDialog () {
      this.$emit('update:quizCreatorDialog', false)
      Object.assign(this.$data, this.initial())
    },
    populateSearchResult (e) {
      this.hasSearchResult = e
    },
    fetch_KIs () {
      const payload = {
        topics_selected: this.topicsSelected
      }
      this.$store.dispatch('app/FETCH_KIS', payload, { root: true })
    }
  }
}
</script>
