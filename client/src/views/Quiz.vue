<template>
  <v-container id="quiz_details_view">
    <v-layout row column wrap justify-center>
      <v-row>
      </v-row>
      <v-row :class="'d-flex ' + (isMobile ? 'flex-column':'') ">
        <v-col lg="8" sm="12" md="12" rows="10">
          <template>
            <v-card color="grey lighten-3" class="rounded-0" elevation="0">
              <v-card-title>
                <h3> Graded report cards </h3>
              </v-card-title>
              <v-card-text>
                <v-data-table
                  :headers="headers"
                  :items="studentsList"
                  :items-per-page="5"
                  class="elevation-1"
                  color="grey lighten-3"
                >
                  <template v-slot:item.email="{ item }">
                    <p :class="item.gradeId === null ? 'text--disabled' : ''">{{ item.email }}</p>
                  </template>
                  <template v-slot:item.score="{ item }">
                    <p v-if="item.score === null" class="text--disabled">N/A</p>
                    <p v-else>{{ item.score }}</p>
                  </template>
                  <template v-slot:item.gradeId="{ item }">
                    <p v-if="item.gradeId === null" class="m-0"> - </p>
                    <a v-else :href="'/report_card/' + item.gradeId" class="text-decoration-none" target="new">
                      <span>
                        <v-icon>mdi-open-in-new</v-icon>
                        View here
                      </span>
                    </a>
                  </template>
                  <template v-slot:item.actions="{ item }">
                    <a v-if="item.gradeId !== null">
                      <v-tooltip bottom open-on-hover>
                        <template v-slot:activator="{ on, attrs }">
                            <v-icon
                              v-bind="attrs"
                              v-on="on"
                              v-on:click="sendStudentReportCard(item.gradeId)"
                            >mdi-email-send</v-icon>
                        </template>
                        <span>Send report card to student as PDF.</span>
                      </v-tooltip>
                    </a>
                  </template>
                </v-data-table>
              </v-card-text>
            </v-card>
          </template>
        </v-col>
        <v-col lg="4" sm="12" md="12">
          <v-col cols="10">
            <h4 class="text-h6" v-text="quizName"></h4>
            <div class="d-flex flex-row justify-space-between">
              <div class="d-flex flex-row align-center">
                <p class="my-4 mx-2 py-1 text-caption">Set quiz as private/public</p>
                <v-menu
                  offset-x
                  offset-y
                  open-on-hover
                  max-width="9rem"
                  max-height="12rem"
                  :close-on-content-click="false"
                  :nudge-width="20"
                  content-class="yellow p-2 lighten-3"
                  v-model="showQuizTogglePopover"
                >
                  <template v-slot:activator="{ on, attrs }">
                    <v-icon
                      small
                      v-bind="attrs"
                      v-on="on">mdi-help-circle-outline</v-icon>
                  </template>
                  <p class="text-caption font-weight-medium">
                    Students need to be part of a class to take a quiz. Public Quizzes can be taken by non-member students. Please be careful switching between public and private quizzes.</p>
                </v-menu>
              </div>
              <v-switch
                  text
                  hint="Toggle between public and private quiz"
                  :input-value="private_"
                  @change="update_quiz">
              </v-switch>
            </div>
          </v-col>
          <v-divider style="width: 100%;"></v-divider>
          <v-card color="grey lighten-4" class="rounded-0" elevation="1">
            <v-card-title>
              <p class="text-caption">Quiz Activities</p>
            </v-card-title>
            <v-divider></v-divider>
            <v-card-actions>
              <v-btn
                color="black lighten-4"
                text
              >
                More actions
              </v-btn>
              <v-spacer></v-spacer>
              <v-btn
                icon
                fab
                x-small
                elevation="2"
                outlined
                @click="show = !show"
              >
                <v-icon>{{ show ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
              </v-btn>
            </v-card-actions>
            <v-expand-transition>
              <div v-show="show">
                <v-card-text>
                  <v-row >
                    <v-col>
                      <a @click="handlePDFGeneration()">
                        Export as PDF
                      </a>
                    </v-col>
                  </v-row>
                </v-card-text>
              </div>
            </v-expand-transition>
          </v-card>
        </v-col>
      </v-row>
    </v-layout>
  </v-container>
</template>

<script>
import Api from '@/service/Api'
import { createNamespacedHelpers } from 'vuex'

const { mapGetters, mapActions } = createNamespacedHelpers('quiz')
const { mapGetters: classRoomGetters } = createNamespacedHelpers('classrooms')

export default {
  name: 'Quiz',
  data () {
    return {
      headers: [
        {
          text: 'Student Email',
          align: 'left',
          sortable: false,
          value: 'email'
        },
        {
          text: 'Score',
          align: 'left',
          sortable: false,
          value: 'score'
        },
        {
          text: 'Report card',
          align: 'left',
          sortable: false,
          value: 'gradeId'
        },
        {
          text: '',
          align: 'left',
          sortable: false,
          value: 'actions'
        }
      ],
      exportableLinks: [
        {
          title: 'PDF',
          action: () => this.handlePDFGeneration()
        }
      ],
      dialog: false,
      showQuizTogglePopover: false,
      show: false,
      items: []
    }
  },
  mounted: function () {
    // TODO: Finalize loading and rendering the quiz
    // then move to making the session get request.
    // this.$store.dispatch('quiz/LOAD_QUIZ', this.$route.params.uuid)
    // this.$store.dispatch('quiz/FETCH_GRADEDQUIZZES', this.$route.params.uuid)

    this.loadQuiz(this.$route.params.uuid)
    this.fetchGradedQuizzes(this.$route.params.uuid)
  },
  computed: {
    quiz_uuid () {
      return this.$route.params.uuid
    },
    ...mapGetters({
      subject: 'subject',
      uuid: 'uuid',
      quizName: 'name',
      quizQuestions: 'quizQuestions',
      gradedQuizzes: 'gradedQuizzes',
      private_: 'private_'
    }),
    ...classRoomGetters({
      currentClassroom: 'GETCURRENTCLASS'
    }),
    isMobile: function () {
      return ['md', 'sm', 'xs'].includes(this.$vuetify.breakpoint.name)
    },
    studentsList: function () {
      let studentsList = []
      for (const student of this.currentClassroom.students) {
        const studentEmail = student.email
        const studentIndex = this._.findIndex(this.gradedQuizzes, (quizGrade) => { return quizGrade.email === studentEmail })
        let studentGradeIdOrNull = null
        let studentGradeScoreOrNull = null
        if (studentIndex !== -1) {
          studentGradeIdOrNull = this.gradedQuizzes[studentIndex].gradeId || null
          studentGradeScoreOrNull = this.gradedQuizzes[studentIndex].score || null
        }

        const quizStudentobj = {
          email: studentEmail,
          gradeId: studentGradeIdOrNull,
          score: studentGradeScoreOrNull
        }
        studentsList = this._.concat(studentsList, quizStudentobj)
      }
      return studentsList
    }
  },

  methods: {
    ...mapActions({
      sendReportCard: 'SENDSTUDENTREPORTCARD',
      loadQuiz: 'LOAD_QUIZ',
      fetchGradedQuizzes: 'FETCH_GRADEDQUIZZES',
      updateQuiz: 'UPDATE_QUIZ'
    }),
    handlePDFGeneration () {
      Api.post(`/class_quiz/${this.quiz_uuid}/generate`, {
        type: 'pdf'
      })
    },
    hasGradedQuiz (grades) {
      return grades && grades.length !== 0
    },
    sendStudentReportCard (gradeUUID) {
      this.sendReportCard(gradeUUID)
    },
    update_quiz (e) {
      this.updateQuiz({
        quizUUID: this.quiz_uuid,
        name: this.quizName,
        private: e || false
      })
    }
  }
}
</script>
