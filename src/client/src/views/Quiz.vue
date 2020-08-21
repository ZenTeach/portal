<template>
  <v-container id="quiz_details_view">
    <v-layout row column wrap justify-center>
      <v-row>
        <v-col cols="12" lg="5">
          <a :href="'../quiz_view/' +  uuid">
            Open Quiz in Browser
          </a>
        </v-col>

        <v-col cols="12" lg="5">
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
      <v-dialog
        v-model="dialog"
        scrollable
        persistent :overlay="false"
        max-width="500px"
        transition="dialog-transition"
      >
        <v-card>
          <v-card-title primary-title>
            Google Form generation underway
          </v-card-title>
          <v-card-text>
            Google Form Quiz generation is underway. We need your help configuring the project.
            Please add the following code to the project.

            Steps:
              1. Open the Google Apps Script by following this link
              <span>
                <v-btn fab dark small color="primary" :href=script_url>
                  <v-icon dark>open-in-new</v-icon>
                </v-btn>
              </span>
              2. Head to Resources > Cloud Platform project...
              3. Enter "SomeProjectCode" in the input field and press "SetProject".
              Hit "Confirm".
              4. Finally, press Close to close the dialog.
              When done with the steps, Press the Generate button below and the quiz link will be sent to your email.
          </v-card-text>

          <v-card-action>
            <v-btn color="success" @click="executeGAppsScript">Generate</v-btn>
            <v-btn color="" @click='dialog = false'>Close</v-btn>
          </v-card-action>
        </v-card>
      </v-dialog>

      <v-row>
        <v-col cols="12" rows="10">
          <h3> Graded report cards </h3>
          <v-data-table
            :headers="headers"
            :items="gradedQuizzes"
            hide-actions
            class="elevation-1"
            no-data-text="No graded report cards yet!"
          >
          </v-data-table>
        </v-col>
      </v-row>
    </v-layout>
  </v-container>
</template>

<script>
import Api from '@/service/Api'
import { mapGetters } from 'vuex'

export default {
  name: 'Quiz',
  data () {
    return {
      gFormExportLoading: false,
      exportableLinks: [
        {
          title: 'Google Form',
          action: () => this.handleGFormExport()
        },
        {
          title: 'PDF',
          action: () => this.handlePDFGeneration()
        }
      ],
      script_id: null,
      script_url: null,
      dialog: false,
      items: [],
      headers: [
        {
          text: 'Student Email',
          align: 'start',
          value: 'email'
        },
        {
          text: 'Score',
          value: 'score'
        },
        {
          text: 'Report Card',
          value: 'gradeId'
        }
      ]
    }
  },
  mounted: function () {
    // TODO: Finalize loading and rendering the quiz
    // then move to making the session get request.
    this.$store.dispatch('quiz/LOAD_QUIZ', this.$route.params.id)
    this.$store.dispatch('quiz/FETCH_GRADEDQUIZZES', this.$route.params.id)
    // Promise.all(
    // )
  },
  computed: {
    // quiz_id () {
    //   return this.$route.params.id
    // }
    ...mapGetters({
      subject: 'quiz/subject',
      uuid: 'quiz/uuid',
      quizQuestions: 'quiz/quizQuestions',
      gradedQuizzes: 'quiz/gradedQuizzes'
    })
  },

  methods: {
    handleGFormExport () {
      console.log(this.$gAuth)
      this.$gAuth.getAuthCode()
        .then(authCode => {
          console.log(authCode)
          return Api.post('/teacher/auth/google', { authCode: authCode })
          // on success
        }).then(response => {
          Api.post(`/class_quiz/${this.quiz_id}/generate`, {
            type: 'gform'
          }).then(response => {
            console.log(response)
            // TODO: Set app to loading state
            if (response.status === 200) {
              this.dialog = true
              this.script_id = response.data.ScriptId
              this.script_url = `https://script.google.com/d/${this.script_id}/edit`
            }
          })
        })
    },
    executeGAppsScript () {
      Api.get(`/class_quiz/${this.quiz_id}/${this.script_id}/generate/execute`)
        .then((response) => {
          console.log(response)
        })
    },
    handlePDFGeneration () {
      Api.post(`/class_quiz/${this.quiz_id}/generate`, {
        type: 'pdf'
      }).then((response) => {
        // TODO: show success/error message
        console.log(response)
      })
    }
  }
}
</script>
