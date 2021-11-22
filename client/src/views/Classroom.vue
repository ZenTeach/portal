<template>
  <v-container>
    <v-layout row column wrap justify-center v-if="$route.name == 'Classroom'">
      <v-flex sm-8 md-10 lg-10 class="ma-6">
        <span class="text-lg-h5 text-sm-body-2 font-weight-bold text-caption">
          <p>My Quizzes</p>
        </span>
        <v-data-table
          :headers="headers"
          :items="current_class.quizzes"
          :items-per-page="5"
          class="elevation-1"
          :footer-props="{
              showFirstLastPage: true,
              firstIcon: 'mdi-arrow-collapse-left',
              lastIcon: 'mdi-arrow-collapse-right',
              prevIcon: 'mdi-minus',
              nextIcon: 'mdi-plus'
            }" >
          <template v-slot:item.name="props">
            <div class="d-flex justify-left">
              <a :href="'/quiz/' +  props.item.uuid" class="d-inline-block mx-1">
                <v-icon medium color="primary" elevation="12">mdi-open-in-app</v-icon>
              </a>
              <v-edit-dialog
                :return-value.sync="props.item.name"
                class="d-inline-block"
                @save="save(props.item.name, props.item.uuid)"
                @cancel="cancel"
                @open="open"
                @close="close">
                {{ props.item.name }}
                <template v-slot:input>
                  <v-text-field
                    v-model="props.item.name"
                    :rules="[max256chars]"
                    label="Edit"
                    single-line
                    class="d-inline"
                    counter
                  >
                  </v-text-field>
                </template>
              </v-edit-dialog>
            </div>
          </template>
          <template v-slot:item.status="{ item }">
            <v-chip :color="statusToColor[item.status]">{{ item.status }}</v-chip>
          </template>
          <template v-slot:item.created_at="{item}">
            <p>
              {{ item.created_at | formatDate }}
            </p>
          </template>
          <template v-slot:footer>
            <v-dialog v-model="dialog" max-width="1000px" persistent>
              <template v-slot:activator="{ on }">
                <v-btn color="primary" right dark class="ma-4 pa-2" v-on="on">
                  <span class="text-caption center d-flex justify-center align-center">
                    <v-icon dark>mdi-plus</v-icon> Create a quiz
                  </span>
                </v-btn>
              </template>
              <quiz-creator v-on:update:quizCreatorDialog="closeQuizCreatorDialog"/>
            </v-dialog>
          </template>
        </v-data-table>
      </v-flex>

      <v-flex sm-8 md-10 lg-10 class="ma-6">
        <student-list v-bind:students="current_class.students" />
      </v-flex>
    </v-layout>
    <keep-alive v-else>
      <router-view></router-view>
    </keep-alive>
  </v-container>
</template>

<script>
import MaterialChartCard from '@/components/ChartCard'
import StudentList from '@/components/StudentList'
import QuizCreator from '@/components/QuizCreator'
import { createNamespacedHelpers } from 'vuex'
import moment from 'moment'
import Api from '@/service/Api'

const { mapGetters, mapActions } = createNamespacedHelpers('classrooms')
const { mapMutations } = createNamespacedHelpers('app')

export default {
  name: 'Classroom',
  components: {
    MaterialChartCard,
    StudentList,
    QuizCreator
  },
  mounted () {
    if (this.$route.name === 'Classroom') {
      this.getCurrentClass(this.$route.params.id)
    }
  },
  filters: {
    formatDate: function (value) {
      if (!value) return ''
      if (value) {
        return moment(String(value)).format('DD/MM/YYYY')
      }
    }
  },
  computed: {
    ...mapGetters({
      current_class: 'GETCURRENTCLASS'
    })
  },
  watch: {
    dialog: function (val) {
      if (val === true) {
        const subject = this.current_class.subject.name
        this.$store.dispatch('app/FETCH_TOPICS', subject, { root: true })
      }
    }
  },
  data () {
    return {
      snack: false,
      snackColor: '',
      snackText: '',
      max256chars: v => v.length <= 256 || 'Input too long!',
      defaultExamBoard: [
        { value: 'aqa', text: 'AQA', suggested: false },
        { value: 'ocr_gateway', text: 'OCR Gateway', suggested: false },
        { value: 'edexcel', text: 'EdExcel', suggested: false },
        { value: 'ocr_new', text: 'OCR 21st Century', suggested: false },
        { value: 'wjec', text: 'WJEC', suggested: false },
        { value: 'ccea', text: 'CCEA', suggested: false },
        { value: 'eduqas', text: 'Eduqas', suggested: false }
      ],
      headers: [
        {
          text: 'Quiz',
          align: 'left',
          sortable: false,
          value: 'name'
        },
        {
          text: 'Status',
          sortable: false,
          value: 'status'
        },
        // TODO: Use actual proctored date
        {
          text: 'Administered at',
          value: 'created_at'
        }
      ],
      quizzes: [],
      dialog: false,
      statusToColor: {
        created: 'yellow',
        administered: 'green',
        cancelled: 'red'
      },
      emailsSubscriptionChart: {
        data: {
          labels: ['Quiz 1', 'Quiz 2', 'Quiz 3'],
          series: [
            [6.4, 8.3, 6.7]

          ]
        },
        options: {
          axisX: {
            showGrid: false
          },
          low: 0,
          high: 10,
          chartPadding: {
            top: 0,
            right: 5,
            bottom: 0,
            left: 0
          }
        },
        responsiveOptions: [
          ['screen and (max-width: 640px)', {
            seriesBarDistance: 5,
            axisX: {
              labelInterpolationFnc: function (value) {
                return value[0]
              }
            }
          }]
        ]
      }
    }
  },
  methods: {
    ...mapActions({
      getCurrentClass: 'GETCURRENTCLASS'
    }),
    ...mapMutations({
      resetQuestionSearch: 'RESET_QUESTION_SEARCH'
    }),
    closeQuizCreatorDialog () {
      this.dialog = false
      this.resetQuestionSearch()
      this.getCurrentClass(this.$route.params.id)
    },
    save (name, uuid) {
      this.snack = true
      this.snackColor = 'success'
      this.snackText = 'Data saved'
      Api.patch(`/class_quiz/${uuid}`,
        {
          name: name
        })
        .then(function (response) {
        })
    },
    cancel () {
      this.snack = true
      this.snackColor = 'error'
      this.snackText = 'Canceled'
    },
    open () {
      this.snack = true
      this.snackColor = 'info'
      this.snackText = 'Dialog opened'
    },
    close () {
    }
  }
}
</script>
