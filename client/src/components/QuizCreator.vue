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
              ref="topicSelection"
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
              ref="kiSelection"
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
                <v-list-group v-for="[topic, kis] in Object.entries(this.fetchedKIsfromTopic())" :key="topic">
                    <v-icon :key="topic">
                      mdi-checkbox
                    </v-icon>
                    <template v-slot:activator>
                      <v-list-item-title>{{topic}}</v-list-item-title>
                    </template>
                    <v-list-item v-for="ki in kis" :key="ki">
                      <v-list-item-title v-text="ki"></v-list-item-title>
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
const { mapState, mapActions, mapGetters } = createNamespacedHelpers('app')

export default {
  name: 'QuizCreator',
  components: {
    QuestionSearch,
    QuestionSearchResult
  },
  computed: {
    ...mapGetters({
      getKis: 'getKis'
    }),
    ...mapState({
      questionSearch: state => state.questionSearch,
      questionList: state => state.questionList,
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
  data () {
    return this.initial()
  },
  watch: {
    getKis: function (val) {
      this.knowledgeItems = []
      this.knowledgeItems = this._.flatten(this._.values(this.getKis))
    }
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
        knowledgeItems: [],
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
      this.$store.commit('app/RESET_QUIZ_CREATOR', { root: true })
      Object.assign(this.$data, this.initial())
      this.$refs.topicSelection.reset()
      this.$refs.kiSelection.reset()
      this.$emit('update:quizCreatorDialog', false)
    },
    populateSearchResult (e) {
      this.hasSearchResult = e
    },
    fetch_KIs () {
      const payload = {
        topics_selected: this.topicsSelected
      }
      this.$store.dispatch('app/FETCH_KIS', payload, { root: true })
    },
    fetchedKIsfromTopic () {
      const kis = this.getKis
      const copy = {}
      for (const key in kis) {
        const kiCopy = kis[key]
        copy[key] = this._.intersection(kiCopy, this.selectedKnowledgeItems)
      }

      return copy
    }
  }
}
</script>
