<template>
  <v-container fluid>
    <v-layout v-if="!this.private_" justify-center>
      <v-card max-width="800" width="800" class="mx-12 rounded-1 p-3">
        <v-card-title> We've received your answers!</v-card-title>
        <v-card-subtitle> </v-card-subtitle>
        <v-card-text>
          <p>Please save this link to check your results later.</p>
          <code>
            {{ origin_url }}/report_card/{{ session_id }}
            <v-icon small @click="copyToClipboard">mdi-content-copy</v-icon>
          </code>

        </v-card-text>
      </v-card>
    </v-layout>
    <v-layout v-else>
      <v-row class="ma-1 pa-2 white" max-width="300px">
        <v-col>
          <div class="mx-auto img-container">
            <v-img src="../assets/completed.png" class="" />
          </div>
        </v-col>
        <v-col justify="center" class="d-flex align-center">
          <p
            class="text-align text-lg-h3 text-sm-h3 text-md-h3 text--lighten-4"
          >
            Your quiz has been submitted!
            <br />
            <v-spacer></v-spacer>
            <router-link to="/" class="text-sm-body-2">Close page</router-link>
          </p>
        </v-col>
      </v-row>
    </v-layout>
  </v-container>
</template>

<script>
import { createNamespacedHelpers } from 'vuex'

const { mapGetters, mapActions } = createNamespacedHelpers('quiz')
export default {
  name: 'QuizSubmitView',
  data () {
    return {}
  },
  computed: {
    quiz_uuid: function () {
      return this.$route.params.quiz_uuid
    },
    ...mapGetters({
      quizName: 'name',
      uuid: 'uuid',
      subject: 'subject',
      private_: 'private_'
    }),
    session_id: function () {
      return window.localStorage.getItem('session_id')
    },
    origin_url: function () {
      return window.location.origin
    },
    anonymous_student_email: function () {
      return window.localStorage.getItem('anonymous_student_email')
    },
    anonymous_student_password: function () {
      return window.localStorage.getItem('anonymous_student_password')
    }
  },
  mounted: function () {
    // load quiz info
    if (this._.isEmpty(this.subject) && this._.isEmpty(this.quizName)) {
      this.loadQuiz(this.quiz_uuid)
    }
  },
  methods: {
    ...mapActions({
      loadQuiz: 'LOAD_QUIZ'
    }),
    copyToClipboard (e) {
      navigator.clipboard.writeText(e.target.parentElement.innerText)
    }
  }
}
</script>
<style>
.img-container {
  width: 300px;
  height: 300px;
  background-color: #fff;
  & > img {
    object-fit: fill;
  }
}
</style>
