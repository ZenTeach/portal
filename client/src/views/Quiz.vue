<template>
  <v-container id="quiz_details_view">
    <v-layout row column wrap justify-center>
      <v-row>
      </v-row>
      <v-row :class="'d-flex ' + (isMobile ? 'flex-column':'') ">
        <v-col lg="8" sm="12" md="12" rows="10">
          <template v-if="this.hasGradedQuiz(this.gradedQuizzes)">
            <v-card color="grey lighten-3" class="rounded-0" elevation="1">
              <v-card-title>
                <h3> Graded report cards </h3>
              </v-card-title>
              <v-card-text>
                <v-data-table
                  :headers="headers"
                  :items="gradedQuizzes"
                  :items-per-page="5"
                  class="elevation-1"
                  color="grey lighten-3"
                >
                  <template v-slot:item.gradeId="{ item }">
                    <a :href="'/report_card/' + item.gradeId" class="text-decoration-none" target="new">
                      <span>
                        <v-icon>mdi-open-in-new</v-icon>
                        View here
                      </span>
                    </a>
                  </template>
                  <template v-slot:item.actions="{ item }">
                    <a>
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
          <template v-else>
            <v-card color="grey lighten-3" class="rounded-0" elevation="1">
              <v-card-title>
                <p class="text-h5"> Graded report cards </p>
              </v-card-title>
              <v-divider></v-divider>
              <v-card-text>
                <v-banner>
                  <v-icon
                    slot="icon"
                    color="yellow darken-4"
                    size="24"
                  >
                    mdi-note-text-outline
                  </v-icon>
                  <p class="text-body-2 text-sm-body-2 text-md-body-2 text-lg-h5 my-5">
                    Quizzes haven't been graded yet!
                  </p>
                </v-banner>
              </v-card-text>
            </v-card>
          </template>
        </v-col>
        <v-col lg="4" sm="12" md="12">
          <v-card color="grey lighten-3" class="rounded-0" elevation="1">
            <v-card-title>
              <p class="text-h6" v-text="quizName"></p>
            </v-card-title>
            <v-col cols="8">
              <p>Set quiz private</p>
              <v-switch :input-value="private_" @change="update_quiz">
              </v-switch>
            </v-col>
            <v-card-subtitle>
              <p class="text-caption">Quiz Activities</p>
            </v-card-subtitle>
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
                <v-divider></v-divider>

                <v-card-text>
                  <v-row >
                    <v-col>
                      <a :href="'../quiz_view/' +  uuid">
                        Open Quiz in Browser
                      </a>
                    </v-col>
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
      script_id: null,
      script_url: null,
      dialog: false,
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
    isMobile: function () {
      return ['md', 'sm', 'xs'].includes(this.$vuetify.breakpoint.name)
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
