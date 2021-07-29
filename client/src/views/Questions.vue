<template>
  <v-container fluid>
    <v-flex xs12 sm12 md12 lg12>
      <v-row >
        <v-col cols="9">
          <v-sheet class="grey lighten-3">
            <div class="w-100">
                  <v-text-field
                    label="SearchInput"
                    placeholder="Question.."
                    @click:append="searchEventListener"
                    v-model="searchInput"
                    append-icon="search"
                    solo
                  ></v-text-field>
            </div>
            <v-responsive
              v-show="showQuestionResults"
              class="overflow-y-auto"
              :max-height.sync="listHeight">
              <div max-height="500">
              <div class="mt-2 mb-n4">
                <span v-show="showQuestionResults" class="mt-n2 mb-n4">
                  <v-btn
                    color="white grey--text"
                    @click="hasSearchResult = false"
                    fab
                    small
                    elevation="0"
                    dark>
                    <h1 class="heading-1" >&times;</h1>
                  </v-btn>
                </span>
              </div>
                <div v-for="(question, idx) in questionSearchList" :key="idx">
                  <v-lazy
                    v-model="question.isActive"
                    :options="{
                      threshold: .5
                    }"
                    :min-height.sync="itemHeight"
                    transition="fade-transition">
                    <div class="white py-3 px-3">
                      <v-row>
                        <v-col cols="10">
                          <h4>{{ question.question }}</h4>
                            <v-chip color="green lighten-5 text-truncate text-center" class="mx-1" small>{{question.topic}}</v-chip>
                            <v-chip color="pink lighten-5 text-truncate text-center" class="mx-1" small>{{question.knowledge_item}}</v-chip>
                          </v-col>
                        <v-col cols="2">
                          <v-btn color="white" elevation="0" @click="editItem({ item: question })">
                            <v-icon small>mdi-pencil</v-icon>
                          </v-btn>
                        </v-col>
                      </v-row>
                      <v-spacer></v-spacer>
                    </div>
                  </v-lazy>
                </div>
              </div>
            </v-responsive>
            <v-card max-width="200px" class="white darken-4 question_search_filter" v-show="showFilter">
              <v-card-title>
                <v-spacer></v-spacer>
                <span class="caption text-semibold">Filters</span>
              </v-card-title>
              <v-card-text>
                <v-select
                  :items="topics"
                  ref="topicSelection"
                  required
                  multiple
                  chips
                  background-color=""
                  class="text-caption"
                  @change="fetch_KIs()"
                  label="Topic: "
                  v-model="selectedTopic"
                ></v-select>
                <v-spacer class="ma-3 mb-3"></v-spacer>

                <v-select
                  label="Knowledge Items: "
                  multiple
                  ref="kiSelection"
                  chips
                  required
                  :items="knowledgeItems"
                  v-model="selectedKnowledgeItems"
                ></v-select>
              </v-card-text>
            </v-card>
           </v-sheet>
        </v-col>
        <v-col cols="3">
          <router-link to="/question/create" >
            <v-btn color="primary" class="float-right mx-4" dark>Create a question</v-btn>
          </router-link>
        </v-col>
        </v-row>
        <v-row>
        <v-col>
          <material-card>
            <template v-slot:header>
              <div class="px-3 d-flex align-center">
                <h4 class="title font-weight-light mb-2">Question Lists</h4>
                <v-spacer></v-spacer>

              </div>
            </template>
            <div>
              <question-search-result
                :resultSet='this.questionList'
                :selectable='false'
                :show_user_created_badge='false'
                no_data_text='User library is empty 📭'
              >
                <template v-slot:extra_actions="itemSlotProps">
                  <v-icon
                    medium
                    class="m-2"
                    @click.stop.capture="openDeleteConfirmationDialog(itemSlotProps)"
                  >
                    mdi-trash-can-outline
                  </v-icon>
                  <v-icon medium class="m-2" @click.stop="editItem(itemSlotProps)">
                    mdi-pencil
                  </v-icon>
                </template>
              </question-search-result>
            </div>
          </material-card>
        </v-col>
      </v-row>
      <v-dialog
        v-model="deleteConfirmationDialog"
        scrollable
        persistent
        :overlay="false"
        max-width="500px"
        transition="dialog-transition"
      >
        <material-card title="⚠ Deleting this question is irreversible.">
          <v-card-text>
            <h3 class="mx-5"> Are you sure you want to delete the question? </h3>
          </v-card-text>

          <v-card-actions>
            <v-btn color="primary" @click="processDeletion()">Delete</v-btn>
            <v-btn color="error" @click="deleteConfirmationDialog = false">Cancel</v-btn>
          </v-card-actions>
        </material-card>
      </v-dialog>
    </v-flex>
  </v-container>
</template>
<script>

import MaterialCard from '@/components/MaterialCard'
import QuestionSearch from '@/components/QuestionSearch'
import QuestionSearchResult from '@/components/QuestionSearchResult'
import { createNamespacedHelpers } from 'vuex'

const { mapActions, mapGetters, mapMutations } = createNamespacedHelpers('questions')
const { mapActions: classroomAction } = createNamespacedHelpers('classrooms')
const { mapGetters: appGetters, mapActions: appActions, mapMutations: appMutations } = createNamespacedHelpers('app')

export default {
  name: 'Questions',
  components: {
    MaterialCard,
    QuestionSearch,
    QuestionSearchResult
  },
  mounted: function () {
    this.resetQuestionSearch()
    this.fetchQuestions()
    this.fetchClasses()
    this.fetchTopics(this.subject)
    this.resetQuestions()
    this.fetchKis({
      topics_selected: this.topics
    })
    this.knowledgeItems = []
    this.knowledgeItems = this._.flatten(this._.values(this.getKis))
  },
  created: function () {
    // re-calc on screen resize
    window.addEventListener('resize', () => {
      this.calcRowsPerPage()
    })
  },
  data: function () {
    return {
      subject: 'Chemistry',
      topicsSelected: [],
      selectedKnowledgeItems: [],
      knowledgeItems: [],
      searchInput: '',
      selectedTopic: '',
      hasSearchResult: true,
      showFilter: false,
      user_created: false,
      deleteConfirmationDialog: false,
      deletableItemId: null,
      rpp: 3
    }
  },
  watch: {
    getKis: function (val) {
      this.knowledgeItems = []
      this.knowledgeItems = this._.flatten(this._.values(this.getKis))
    }
  },
  computed: {
    ...appGetters({
      topics: 'getTopics',
      getKis: 'getKis',
      questionSearchList: 'getQuestionResult',
      getError: 'getError'
    }),
    ...mapGetters({
      questionList: 'QUESTIONLIST'
    }),
    listHeight: function () {
      return (this.itemHeight * this.rowsPerPage) + 50
    },
    showQuestionResults: function () {
      return this.hasSearchResult && this.questionSearchList.length > 0
    },
    rowsPerPage () {
      return this.rpp
    },
    itemHeight () {
      switch (this.$vuetify.breakpoint.name) {
        case 'xs': return 50
        case 'sm': return 50
        case 'md': return 75
        case 'lg': return 100
        case 'xl': return 150
      }
    }
  },
  methods: {
    ...appActions({
      fetchTopics: 'FETCH_TOPICS',
      fetchKis: 'FETCH_KIS'
    }),
    ...appMutations({
      resetQuestionSearch: 'RESET_QUESTION_SEARCH'
    }),
    questionTypeMapping (type) {
      const types = {
        1: 'Multiple Choice',
        2: 'Short Answer',
        3: 'Long Answer'
      }
      return types[type]
    },
    calcRowsPerPage () {
      const container = document.getElementById('search_result')
      const minItemHeight = 170
      if (container) {
        const containerHeight = parseInt(container.clientHeight, 0)
        this.rpp = Math.floor(containerHeight / minItemHeight)
      } else {
        this.rpp = 4
      }
    },
    ...mapActions({
      fetchQuestions: 'GETQUESTIONS',
      deleteQuestion: 'DELETEQUESTION'
    }),
    ...classroomAction({
      fetchClasses: 'GETCLASSES'
    }),
    ...mapMutations({
      setCurrentQuestion: 'SET_CURRENTQUESTION',
      resetQuestions: 'RESET_QUESTIONS'
    }),
    fetch_KIs: function () {
      const payload = {
        topics_selected: this.selectedTopic
      }
      this.$store.dispatch('app/FETCH_KIS', payload, { root: true })
    },
    openDeleteConfirmationDialog (e) {
      this.deletableItemId = e.item.id
      this.deleteConfirmationDialog = true
    },
    searchEventListener () {
      this.resetQuestionSearch()
      this.searchInput = this.searchInput.trim()
      this.$store.dispatch('app/QUERY_QUESTIONS', {
        query: this.searchInput,
        subject: this.subject,
        topic: this.topics,
        knowledge_item: this.knowledgeItems
      }, { root: true })
      this.hasSearchResult = true
    },
    processDeletion () {
      this.deleteQuestion(this.deletableItemId)
      setTimeout(() => {
        this.deleteConfirmationDialog = false
      }, 200)
    },
    editItem (item) {
      this.setCurrentQuestion(item.item)
      this.$router.push('/question/edit')
    },
    populateSearchResult (e) {
      this.hasSearchResult = true
    },
    toggleFilterView () {
      this.showFilter = !this.showFilter
    }
  }
}
</script>

<style scoped>
.question_search_filter {
  z-index: 100 !important;
  position: absolute !important;
  top: 6em !important;
}
</style>
