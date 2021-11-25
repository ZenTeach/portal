<template>
  <v-container fluid>
    <v-dialog v-model="dialog" max-width="1000px" persistent>
      <v-card class="mx-auto px-auto" outlined>
        <v-card-title class="font-weight-light"> Quiz Procotor </v-card-title>
        <v-card-text class="headline font-weight-bold">
          <div>
            <p> Please enter your email to start your quiz: </p>
            <v-text-field
              single-line
              prepend-icon="email"
              outline
              required
              v-model="studentEmail"
            ></v-text-field>
            <v-banner
              color="error"
              v-model="showSessionErrors"
              icon="warning"
            >
              <div class="d-flex align-content-center flex-wrap ml-auto">
                <p class="white--text mt-0 mb-2 font-weight-light text-h6 text-md-h5">
                  {{ (error &&  error.message) || "We've run into an error, please try again later." }}
                </p>
                <v-btn
                  text
                  color="white"
                  outlined
                  class="mb-2 text-md-h6"
                  @click="showSessionErrors=!showSessionErrors"
                >
                  Dismiss
                </v-btn>
              </div>
            </v-banner>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-btn color="primary lighten-2" outlined class="mr-4" @click="startQuizSession" :loading="loading">Proceed</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-row class="ma-lg-4 pa-lg-3">
      <input type="hidden" />
      <v-col class="ma-lg-2">
        <h1>{{ quizTitle }}</h1>
      </v-col>
    </v-row>
    <v-row class="mx-lg-10 pa-lg-3">
      <v-col>
      <template v-for="(question, q_idx) in quiz_questions" >
        <v-card :key="q_idx" class="ma-2" ref="">
          <input type="hidden" :value="question['id']"  ref="question_id"/>
          <v-card-text ref="question_">
            <h3> {{ question.question }} </h3>
            <v-radio-group>
              <template v-for="(choice, idx) in question.choices">
                <div :id="'div'+idx" :key="'div'+idx" class="d-flex">
                    <input type="radio"
                      :key="idx"
                      :name="question.id"
                      :value="choice.uuid"
                      @input.self="appendToSelection"/>
                    <label :for="choice.value" key="'label'+idx">
                      <span class="text-sm-body-2">
                        {{choice.value}}
                      </span>
                    </label >
                  </div>
                </template>
              </v-radio-group>
          </v-card-text>
        </v-card>
      </template>
      </v-col>
    </v-row>

    <v-row class="mx-10 pa-5">
      <v-btn :disabled="!isValid" color="success" @click="submit()">
        Submit Quiz
      </v-btn>
    </v-row>

    <v-dialog v-model="hasSubmitted" max-width="100vw" max- persistent>
      <v-row class="ma-1 pa-2 white">
        <v-col>
          <div class="mx-auto img-container">
            <v-img src="../assets/completed.png" class="" />
          </div>
        </v-col>
        <v-col justify="center" class="d-flex align-center">
          <p class="text-align text-lg-h1 text-sm-h1 text-md-h1 text--lighten-4">
          Congrats! Your quiz has been submitted!
          <br />
          <v-spacer></v-spacer>
          <router-link to="/" class="text-sm-caption">Close page</router-link>
          </p>
        </v-col>
      </v-row>
    </v-dialog>
  </v-container>
</template>

<script>
import { createNamespacedHelpers } from 'vuex'

const { mapGetters } = createNamespacedHelpers('quiz')
export default {
  name: 'QuizView',
  data () {
    return {
      dialog: true,
      studentEmail: '',
      selectedChoices: {},
      showSessionErrors: false,
      completedModal: false
    }
  },
  computed: {
    ...mapGetters({
      quizUUID: 'uuid',
      quiz_questions: 'quizQuestions',
      quizTitle: 'name',
      hasSubmitted: 'hasSubmitted',
      error: 'error',
      hasError: 'errorState',
      loading: 'loading',
      hasStarted: 'has_started'
    }),
    routeId () {
      return this.$route.params.id
    },
    selectedChoicesLength () {
      return Object.keys(this.selectedChoices).length
    },
    isValid () {
      return !this._.isEmpty(this.selectedChoices) &&
        this.selectedChoicesLength === this.quiz_questions.length
    },
    qid () {
      if (this.quizUUID == null) {
        return this.quizUUID
      } else {
        return this.routeId
      }
    },
    setDialogState () {
      this.dialog = !this.hasStarted || this.hasError
    }
  },
  watch: {
    hasError: function (val) {
      if (val) {
        this.showSessionErrors = this.hasError
      }
    }
  },
  methods: {
    appendToSelection (event) {
      // Properly handle vue updates
      this.$set(this.selectedChoices, event.target.name, event.target.value)
    },
    submit () {
      const payload = this._collect_submission()
      this.$store.dispatch('quiz/SUBMIT_QUIZ', payload, { root: true })
      if (this.hasSubmitted) {
        this.completedModal = true
      }
    },
    _collect_submission () {
      const data = []
      for (const [k, v] of Object.entries(this.selectedChoices)) {
        data.push(
          {
            questionID: k,
            Choice_answer: v
          }
        )
      }

      return {
        QuizId: this.quizUUID,
        StudentEmail: this.studentEmail,
        data: data
      }
    },
    startQuizSession () {
      this.$store.dispatch('quiz/START_QUIZ', {
        studentEmail: this.studentEmail,
        quizUUID: this.qid
      }, { root: true })
    }
  },
  beforeDestroy: function () {
    this.$store.commit('quiz/UNSET_QUIZ_SUBMISSION', {}, { root: true })
  }
}
</script>

<style lang="scss" scoped>
@supports(-webkit-appearance: none) or (-moz-appearance: none) {
  div > input[type='radio'] {
    display: inline-block;
    padding: 0.3rem;
  }
  input[type='checkbox'],
  input[type='radio'] {
    --active: #275EFE;
    --active-inner: #fff;
    --focus: 2px rgba(39, 94, 254, .3);
    --border: #BBC1E1;
    --border-hover: #275EFE;
    --background: #fff;
    --disabled: #F6F8FF;
    --disabled-inner: #E1E6F9;
    -webkit-appearance: none;
    -moz-appearance: none;
    height: 21px;
    outline: none;
    display: inline-block;
    vertical-align: top;
    position: relative;
    margin: 0;
    cursor: pointer;
    border: 1px solid var(--bc, var(--border));
    background: var(--b, var(--background));
    transition: background .3s, border-color .3s, box-shadow .2s;
    &:after {
      content: '';
      display: block;
      left: 0;
      top: 0;
      position: absolute;
      transition: transform var(--d-t, .3s) var(--d-t-e, ease), opacity var(--d-o, .2s);
    }
    &:checked {
      --b: var(--active);
      --bc: var(--active);
      --d-o: .3s;
      --d-t: .6s;
      --d-t-e: cubic-bezier(.2, .85, .32, 1.2);
    }
    &:disabled {
      --b: var(--disabled);
      cursor: not-allowed;
      opacity: .9;
      &:checked {
        --b: var(--disabled-inner);
        --bc: var(--border);
      }
      & + label {
        cursor: not-allowed;
      }
    }
    &:hover {
      &:not(:checked) {
        &:not(:disabled) {
          --bc: var(--border-hover);
        }
      }
    }
    &:focus {
      box-shadow: 0 0 0 var(--focus);
    }
    &:not(.switch) {
      width: 21px;
      &:after {
        opacity: var(--o, 0);
      }
      &:checked {
        --o: 1;
      }
    }
    & + label {
      font-size: 1rem;
      line-height: 1.5rem;
      display: inline-block;
      vertical-align: top;
      cursor: pointer;
      margin-left: 4px;
    }
  }
  input[type='checkbox'] {
    &:not(.switch) {
      border-radius: 7px;
      &:after {
        width: 5px;
        height: 9px;
        border: 2px solid var(--active-inner);
        border-top: 0;
        border-left: 0;
        left: 7px;
        top: 4px;
        transform: rotate(var(--r, 20deg));
      }
      &:checked {
        --r: 43deg;
      }
    }
    &.switch {
      width: 38px;
      border-radius: 11px;
      &:after {
        left: 2px;
        top: 2px;
        border-radius: 50%;
        width: 15px;
        height: 15px;
        background: var(--ab, var(--border));
        transform: translateX(var(--x, 0));
      }
      &:checked {
        --ab: var(--active-inner);
        --x: 17px;
      }
      &:disabled {
        &:not(:checked) {
          &:after {
            opacity: .6;
          }
        }
      }
    }
  }
  input[type='radio'] {
    border-radius: 50%;
    &:after {
      width: 19px;
      height: 19px;
      border-radius: 50%;
      background: var(--active-inner);
      opacity: 0;
      transform: scale(var(--s, .7));
    }
    &:checked {
      --s: .5;
    }
  }
}
.img-container {
  width: 300px;
  height: 300px;
  background-color: #fff;
  & > img {
    object-fit: fill;
  }
}
</style>
