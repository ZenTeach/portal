<template>
  <v-container id="quiz_details_view">
    <v-layout row column wrap justify-center>
      <v-row>
        <div class="flex-lg-grow-1 flex-sm-grow-0 flex-md-grow-0"></div>
        <v-col lg="2" md="4" sm="6">
          <a :href="'../quiz_view/' +  uuid">
            Open Quiz in Browser
          </a>
        </v-col>

        <v-col lg="2" md="4" sm="6">
          <template>
            <div class="text-center">
                <v-menu bottom offset-y>
                <template v-slot:activator="{ on }">
                <v-btn
                  color="success"
                  dark
                  v-on="on"
                  >
                  <v-icon left>mdi-share-variant</v-icon>
                  Export to:
                  </v-btn>
                </template>

                <v-list>
                  <v-list-item
                  v-for="(item, index) in exportableLinks"
                  :key="index"
                  @click="item.action"
                  >
                  <v-list-item-title>{{ item.title }}</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
            </div>
          </template>
        </v-col>
      </v-row>

      <v-row>
      </v-row>
      <v-divider></v-divider>
      <v-row>
        <v-col cols="12" rows="10">
        <template v-if="this.hasGradedQuiz(this.gradedQuizzes)">
          <h3> Graded report cards </h3>
          <!-- <v-simple-table>
            <template v-slot:default v-if="gradedQuizzes">
            <tbody>
              <template v-for="item in gradedQuizzes">
                <tr :key="item.email">
                  <td class="tg-cly1" >{{ item.email }}</td>
                  <td class="tg-0lax">{{ item.score }}</td>
                  <td class="tg-0lax">

                  </td>
                  <td class="tg-0lax">
                  </td>
                </tr>
              </template>
            </tbody>
            </template>
          </v-simple-table> -->
          <v-data-table
            :headers="headers"
            :items="gradedQuizzes"
            :items-per-page="5"
            class="elevation-1"
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
        </template>
        <template v-else>
          <h3> Graded report cards </h3>
          <v-banner>
            <v-icon
              slot="icon"
              color="red"
              size="36"
            >
              mdi-note-text-outline
            </v-icon>
            <p class="text-h3 text-sm-h2 text-md-h2 my-5">
              Quizzes haven't been graded yet!
            </p>

              <!-- TODO: Add a button to send quiz to students.
              <template v-slot:actions>
                <v-btn
                  color="primary"
                  text
                >
                  Connecting Settings
                </v-btn>
              </template>
              -->
          </v-banner>
        </template>
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
      quizQuestions: 'quizQuestions',
      gradedQuizzes: 'gradedQuizzes'
    })
  },

  methods: {
    ...mapActions({
      sendReportCard: 'SENDSTUDENTREPORTCARD',
      loadQuiz: 'LOAD_QUIZ',
      fetchGradedQuizzes: 'FETCH_GRADEDQUIZZES'
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
    }
  }
}
</script>
