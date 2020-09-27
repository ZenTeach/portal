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

      <v-row>
      </v-row>
      <v-divider></v-divider>
      <v-row>
        <v-col cols="12" rows="10">
          <h3> Graded report cards </h3>
        <v-simple-table>
          <template v-slot:default>
          <thead>
              <tr>
                <th class="text-left">Student Email</th>
                <th class="text-left">Score</th>
                <th class="text-left">Report card</th>
              </tr>
          </thead>
          <tbody>
            <template v-for="item in gradedQuizzes">
              <tr :key="item.email">
                <td class="tg-cly1" >{{ item.email }}</td>
                <td class="tg-0lax">{{ item.score }}</td>
                <td class="tg-0lax">
                  <a :href="'/report_card/' + item.gradeId" class="text-decoration-none" target="new">
                    <span>
                      <v-icon>mdi-open-in-new</v-icon>
                      View here
                    </span>
                  </a>
                </td>
              </tr>
            </template>
          </tbody>
          </template>
        </v-simple-table>
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
    this.$store.dispatch('quiz/LOAD_QUIZ', this.$route.params.id)
    this.$store.dispatch('quiz/FETCH_GRADEDQUIZZES', this.$route.params.id)
  },
  computed: {
    quiz_id () {
      return this.$route.params.id
    },
    ...mapGetters({
      subject: 'quiz/subject',
      uuid: 'quiz/uuid',
      quizQuestions: 'quiz/quizQuestions',
      gradedQuizzes: 'quiz/gradedQuizzes'
    })
  },

  methods: {
    handlePDFGeneration () {
      Api.post(`/class_quiz/${this.quiz_id}/generate`, {
        type: 'pdf'
      })
    }
  }
}
</script>
