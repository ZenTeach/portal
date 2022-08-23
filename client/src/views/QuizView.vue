<template>
  <v-container fluid>
    <v-layout v-if="loading">
      <v-skeleton-loader
        width="75vw"
        height="60vh"
        class="mx-auto"
        type="heading, list-item, list-item-three-line, actions"
        ></v-skeleton-loader>
    </v-layout>
    <v-layout v-else column>
    <quiz-view-prompt
      :showDialog="dialog"
      :showSessionErrors="showSessionErrors"
      :studentEmail="studentEmail"
      :error="error"
      :loading="loading"
      :proceedAction="startQuizSession"
      />
    <v-row class="ma-lg-4 pa-lg-3">
      <v-col class="ma-lg-2">
        <h1>{{ name }}</h1>
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
                  <v-radio
                      :key="idx"
                      :name="'' + question.id"
                      :value="choice.uuid"
                      :label="choice.value"
                      @click.stop="appendToSelection(question.id, choice.uuid)">
                  </v-radio>
                </div>
              </template>
            </v-radio-group>
          </v-card-text>
        </v-card>
      </template>
      </v-col>
    </v-row>

    <v-row class="mx-10 pa-5">
      <v-btn :disabled="!isValid" :loading="loading" color="success" @click="submit()">
        Submit Quiz
      </v-btn>
    </v-row>
  </v-layout>
  </v-container>
</template>

<script>
import { createNamespacedHelpers } from 'vuex'
import QuizViewPrompt from '@/components/QuizViewComponents/QuizViewPrompt'

const { mapGetters, mapActions } = createNamespacedHelpers('quiz')
const { mapGetters: userGetters } = createNamespacedHelpers('user')
export default {
  name: 'QuizView',
  components: {
    QuizViewPrompt
  },
  data () {
    return {
      studentEmail: '',
      selectedChoices: {},
      showSessionErrors: false
    }
  },
  mounted: function () {
    this.loadQuiz(this.$route.params.id).then(() => {
      this.autoStartQuizSession()
    })
  },
  computed: {
    ...userGetters({
      currentStudent: 'getCurrentUser'
    }),
    ...mapGetters({
      quiz_questions: 'quizQuestions',
      name: 'name',
      hasSubmitted: 'hasSubmitted',
      error: 'error',
      hasError: 'errorState',
      loading: 'loading',
      private_: 'private_',
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
      return this.routeId
    },
    dialog () {
      if (this.private_ === false) {
        return false
      }
      // if quiz has started or has been submitted, don't show dialog
      // regardless of the above case, always show dialog if quiz has error
      return !(this.hasStarted ^ this.hasSubmitted) || this.hasError
    }
  },
  watch: {
    hasError: function (val) {
      if (val !== null || val !== undefined) {
        this.showSessionErrors = this.hasError
      }
    }
  },
  methods: {
    ...mapActions({
      loadQuiz: 'LOAD_QUIZ'
    }),
    appendToSelection (name, value) {
      // Properly handle vue updates
      this.$set(this.selectedChoices, name, value)
    },
    submit () {
      const payload = this._collect_submission()
      this.$store.dispatch('quiz/SUBMIT_QUIZ', payload, { root: true }).then(() => {
        this.$router.push(`/post_submit/${this.$route.params.id}`)
      })
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
        QuizId: this.qid,
        StudentEmail: this.studentEmail,
        data: data
      }
    },
    autoStartQuizSession () {
      if (!this.private_) {
        this.startQuizSession()
      }
    },
    startQuizSession () {
      if (!this.hasStarted) {
        this.$store.dispatch('quiz/START_QUIZ', {
          studentEmail: this.studentEmail,
          quizUUID: this.qid
        }, { root: true })
          .then(() => {
            this.studentEmail = this.currentStudent
          })
      }
    }
  },
  beforeDestroy: function () {
    this.$store.commit('quiz/UNSET_QUIZ_SUBMISSION', {}, { root: true })
  }
}
</script>

<style scoped>
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
