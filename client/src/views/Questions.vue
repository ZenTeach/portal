<template>
  <v-container fluid>
    <v-flex xs12 sm12 md12 lg12>
      <v-row>
        <v-col>
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
                no_data_text='User is library empty 📭'
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
import QuestionSearchResult from '@/components/QuestionSearchResult'
import { createNamespacedHelpers } from 'vuex'

const { mapActions, mapGetters, mapMutations } = createNamespacedHelpers('questions')
const { mapActions: classroomAction } = createNamespacedHelpers('classrooms')

export default {
  name: 'Questions',
  components: {
    MaterialCard,
    QuestionSearchResult
  },
  mounted: function () {
    this.fetchQuestions()
    this.fetchClasses()
  },
  data: function () {
    return {
      deleteConfirmationDialog: false,
      deletableItemId: null
    }
  },
  computed: {
    ...mapGetters({
      questionList: 'QUESTIONLIST'
    })
  },
  methods: {
    ...mapActions({
      fetchQuestions: 'GETQUESTIONS',
      deleteQuestion: 'DELETEQUESTION'
    }),
    ...classroomAction({
      fetchClasses: 'GETCLASSES'
    }),
    ...mapMutations({
      setCurrentQuestion: 'SET_CURRENTQUESTION'
    }),
    openDeleteConfirmationDialog (e) {
      this.deletableItemId = e.item.id
      this.deleteConfirmationDialog = true
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
    }
  }
}
</script>
