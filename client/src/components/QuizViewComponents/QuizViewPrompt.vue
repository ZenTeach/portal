<template>
  <v-dialog v-model="showDialog" max-width="1000px" hide-overlay>
    <v-card class="mx-auto px-auto" outlined>
      <v-card-title class="font-weight-light">
        Start a quizzing session
      </v-card-title>
      <v-card-text class="headline font-weight-bold">
        <div>
          <p>Please enter your email to start your quiz:</p>
          <v-text-field
            single-line
            prepend-icon="email"
            outline
            required
            :value="studentEmail"
          ></v-text-field>
          <v-banner color="error" v-model="showSessionErrors" icon="warning">
            <div class="d-flex align-content-center flex-wrap ml-auto">
              <p
                class="white--text mt-0 mb-2 font-weight-light text-h6 text-md-h5"
              >
                {{
                  error_message ||
                    "We've run into an error, please try again later."
                }}
              </p>
              <v-btn
                text
                color="white"
                outlined
                class="mb-2 text-md-h6"
                @click="toggleError"
              >
                Dismiss
              </v-btn>
            </div>
          </v-banner>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-btn
          color="primary lighten-2"
          outlined
          class="mr-4"
          @click="proceedAction"
          :loading="loading"
          >Proceed</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'QuizViewPrompt',
  props: {
    showDialog: {
      type: Boolean,
      default: false
    },
    showSessionErrors: {
      type: Boolean,
      default: false
    },
    studentEmail: {
      type: String,
      default: ''
    },
    error: {
      type: Object
    },
    loading: {
      type: Boolean
    },
    proceedAction: {
      type: Function
    }
  },
  computed: {
    error_message: function () {
      if (this._.isNull(this.error)) return
      return this.error || this._.get(this.error, 'message')
    }
  },
  methods: {
    toggleError: function () {
      this.showSessionErrors = !this.showSessionErrors
    }
  }
}
</script>
