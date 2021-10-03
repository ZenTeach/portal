<template>
  <v-stepper v-model="curator">
    <v-stepper-header>
      <v-stepper-step
        step="1"
        editable
        :rules="[() => firstStepValidation]"
        :complete="curator > 1">Topic selection</v-stepper-step>

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
              :rules="[validateTopicsSelected]"
            >
              <template v-slot:selection="{ item, index }">
                <v-chip x-small v-if="index < maxTopicLength">
                  <p style="max-width: 16ch;" class="text-caption text-truncate font-weight-bold pt-4">{{ item }}</p>
                </v-chip>
                <span
                  v-if="index >= maxTopicLength"
                  class="grey--text text-caption"
                >
                  (+{{ topicsSelected.length - 1 }} others)
                </span>
              </template>
            </v-select>

            <v-spacer class="ma-3 mb-3"></v-spacer>

            <v-select
              label="Knowledge Items: "
              multiple
              ref="kiSelection"
              chips
              required
              :items="knowledgeItems"
              :rules="[validateSelectedKnowledgeItems]"
              v-model="selectedKnowledgeItems"
            >
              <template v-slot:selection="{ item, index }">
                  <v-chip x-small v-if="index < maxKILength">
                    <v-tooltip bottom>
                      <template v-slot:activator="{ on, attrs }">
                        <p
                          style="max-width: 16ch;"
                          v-bind="attrs"
                          v-on="on"
                          class="text-caption text-truncate font-weight-bold pt-4">{{ item }}</p>
                      </template>
                      <span>{{ item }}</span>
                    </v-tooltip>
                  </v-chip>
                  <span
                    v-if="index >= maxKILength"
                    class="grey--text text-caption"
                  >
                    (+{{ selectedKnowledgeItems.length - 1 }} others)
                  </span>
              </template>
            </v-select>
          </v-card-text>
          <v-card-actions class="justify-space-between px-5">
            <div class="d-flex">
              <v-btn color="primary" v-if="!isMobile" class="mr-2" @click="gotoStep(2, 'firstStepValidation')">Continue</v-btn>
              <v-btn color="success" v-if="!isMobile" @click="createQuizFastTracked()">Finish</v-btn>
              <v-btn color="primary" v-if="isMobile" class="mr-2" @click="gotoStep(2, 'firstStepValidation')">
                <v-icon>mdi-chevron-right</v-icon>
              </v-btn>
              <v-btn color="success" v-if="isMobile" @click="createQuizFastTracked()">
                <v-icon left>mdi-check-all</v-icon>
              </v-btn>
            </div>
            <v-btn @click.native.prevent="closeDialog()" v-if="!isMobile" class="float-left error">Cancel</v-btn>
            <v-btn @click.native.prevent="closeDialog()" v-if="isMobile" class="float-left error">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-stepper-content>
      <v-stepper-content step="2">
        <v-card color="grey lighten-4" class="mx-auto">
          <v-card-title>Search for Questions</v-card-title>
          <v-card-text>
            <question-search :subject="subject" :topics="topicsSelected" :knowledge_items="selectedKnowledgeItems" v-on:update:searchResult="populateSearchResult"/>
            <question-search-result :resultSet="questionSearch" v-show="hasSearchResult">
              <template v-slot:extra_actions="{ item }">
                <v-btn :elevation="0" class="white" :ripple="false" @click.capture.stop="confirmEdit(item)">
                  <v-icon small class="m-2">
                      mdi-pencil
                  </v-icon>
                </v-btn>
              </template>
            </question-search-result>
          </v-card-text>
          <v-card-actions class="justify-space-between px-5">
            <v-btn color="primary" v-if="!isMobile" @click="curator = 3">Continue</v-btn>
            <v-btn color="primary" v-if="isMobile" @click="curator = 3">
              <v-icon>mdi-chevron-right</v-icon>
            </v-btn>
            <v-btn @click.native.prevent="closeDialog()" v-if="!isMobile" class="float-left error">Cancel</v-btn>
            <v-btn @click.native.prevent="closeDialog()" v-if="isMobile" class="float-left error">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-stepper-content>
      <v-stepper-content step="3">
        <v-card color="grey lighten-4" class="mx-auto">
          <v-card-title>Finalize Quiz</v-card-title>
            <v-card-text>
              <p v-if="isMobile"> Quiz is ready to be created! </p>
              <h4 class="text-subtitle-1" v-if="!isMobile">Selected topics & knowledge items</h4>
              <v-list v-if="!isMobile">
                <v-list-group v-for="[topic, kis] in Object.entries(this.fetchedKIsfromTopic())" :key="topic">
                    <v-icon :key="topic">
                      mdi-checkbox
                    </v-icon>
                    <template v-slot:activator>
                      <v-list-item-title class="body-1 text-uppercase font-weight-bold">{{topic}}</v-list-item-title>
                      <v-badge
                        color="success"
                        overlap
                        :content="_.get(questionTopicCount, topic) || 0"
                        :value="_.get(questionTopicCount, topic) || 0"
                      ></v-badge>
                    </template>
                    <v-list-item v-for="ki in kis" :key="ki">
                      <v-list-item-title v-text="ki" class="font-weight-light"></v-list-item-title>
                      <v-chip
                        class="ma-2"
                        close
                        color="success"
                        label
                        x-small
                        outlined>
                          {{ _.get(questionKICount, ki) || 0 }} / {{ questionList.length || 0 }} Questions selected
                      </v-chip>

                      <v-list-item-icon>
                        <v-icon>mdi-checkbox-marked-circle</v-icon>
                      </v-list-item-icon>
                    </v-list-item>
                </v-list-group>
              </v-list>
            </v-card-text>
            <v-card-actions class="justify-space-between px-5">
              <v-btn color="primary" v-if="!isMobile" @click="createQuiz()" :disabled="!formIsValid">Create</v-btn>
              <v-btn color="primary" v-if="isMobile" @click="createQuiz()" :disabled="!formIsValid">
                <v-icon>mdi-check-all</v-icon>
              </v-btn>
              <v-btn @click.native.prevent="closeDialog()" v-if="!isMobile" class="float-left error">Cancel</v-btn>
              <v-btn @click.native.prevent="closeDialog()" v-if="isMobile" class="float-left error">
                <v-icon>mdi-close</v-icon>
              </v-btn>
            </v-card-actions>
          </v-card>
      </v-stepper-content>
    </v-stepper-items>
    <v-dialog
      v-model="confirmQuestionEdit"
      persistent
      max-width="500px"
      transition="dialog-transition"
    >
    <v-card>
      <v-card-title>
        <v-icon color="orange lighten-1" class="mx-1">
          mdi-alert
        </v-icon>
        Confirm editing question
      </v-card-title>
      <hr />
      <v-card-text>
        <p class="body-2 font-weight-normal my-2 mx-2"> Confirming this will take you to a different page for editing
          selected Question
        </p>
      </v-card-text>
      <v-card-actions>
        <div class="flex-grow-1"></div>
        <v-btn color="success" @click="goToQuestionEdit()" outlined>Continue editing</v-btn>
        <v-btn color="error" @click="confirmQuestionEdit=false" text outlined>Cancel</v-btn>
      </v-card-actions>
    </v-card>
    </v-dialog>
  </v-stepper>
</template>

<script>
import QuestionSearch from '@/components/QuestionSearch'
import QuestionSearchResult from '@/components/QuestionSearchResult'
import Api from '@/service/Api'

import { createNamespacedHelpers } from 'vuex'
const { mapState, mapActions, mapGetters, mapMutations: appMutations } = createNamespacedHelpers('app')
const { mapMutations: questionMutations } = createNamespacedHelpers('questions')

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
      return filtered.subject.name
    },
    questionKICount () {
      return this._.countBy(this.questionList, 'knowledge_item')
    },
    questionTopicCount () {
      return this._.countBy(this.questionList, 'topic')
    },
    formIsValid () {
      return this.firstStepValidation && (this.questionList.length > 0)
    },
    maxTopicLength () {
      switch (this.$vuetify.breakpoint.name) {
        case 'xs': return 1
        case 'sm': return 2
        case 'md': return 3
        case 'lg': return 4
        case 'xl': return 5
      }
    },
    maxKILength () {
      switch (this.$vuetify.breakpoint.name) {
        case 'xs': return 3
        case 'sm': return 5
        case 'md': return 7
        case 'lg': return 9
        case 'xl': return 12
      }
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
    ...questionMutations({
      setCurrentQuestion: 'SET_CURRENTQUESTION'
    }),
    ...appMutations({
      resetQuestionSearch: 'RESET_QUESTION_SEARCH'
    }),
    initial () {
      return {
        curator: 1,
        questionSearchResult: [],
        hasSearchResult: false,
        firstStepValidation: true,
        topicsSelected: [],
        knowledgeItems: [],
        selectedKnowledgeItems: [],
        editableQuestion: {},
        confirmQuestionEdit: false
      }
    },
    validateTopicsSelected () {
      return this.topicsSelected.length > 0 || 'You must choose at least one'
    },
    validateSelectedKnowledgeItems () {
      return this.selectedKnowledgeItems.length > 0 || 'You must choose at least one'
    },
    validateStep (dataValueName) {
      const val = (this.topicsSelected.length > 0) && (this.selectedKnowledgeItems.length > 0)
      this._.set(this.$data, dataValueName, val)
    },
    gotoStep (step, validator) {
      this.validateStep(validator)
      this.curator = step
    },
    isMobile: function () {
      return ['md', 'sm', 'xs'].includes(this.$vuetify.breakpoint.name)
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
      this.resetQuestionSearch()
      this.fetchQuestionsFastTracked(
        {
          topics: this.topicsSelected,
          kis: this.selectedKnowledgeItems
        })
        .then(() => {
          this.hasSearchResult = true
          this.curator = 3
        })
    },
    goToQuestionEdit () {
      this.setCurrentQuestion(this.editableQuestion)
      this.resetQuestionSearch()
      this.$router.push('/question/create')
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
    },
    confirmEdit (item) {
      Object.assign(this.editableQuestion, item)
      this.confirmQuestionEdit = true
    }
  }
}
</script>
