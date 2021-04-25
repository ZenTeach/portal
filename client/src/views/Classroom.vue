<template>
  <v-container>
    <v-layout row column wrap justify-center>
      <v-flex sm-8 md-10 lg-10 class="ma-6">
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
            <a :href="'/quiz/' +  props.item.uuid">Quiz {{ props.item.name }}</a>
          </template>
          <template v-slot:item.status="{ item }">
            <v-chip :color="statusToColor[item.status]">{{ item.status }}</v-chip>
          </template>
          <template v-slot:item.created_at="{item}">
            {{ item.created_at | formatDate }}
          </template>
          <template v-slot:footer>
            <v-dialog v-model="dialog" max-width="1000px" persistent>
              <template v-slot:activator="{ on }">
                <v-btn color="primary" right fab dark class="ma-2 pa-2" v-on="on">
                  <v-icon dark>mdi-plus</v-icon>
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
  </v-container>
</template>

<script>
import MaterialChartCard from '@/components/ChartCard'
import StudentList from '@/components/StudentList'
import QuizCreator from '@/components/QuizCreator'
import { createNamespacedHelpers } from 'vuex'

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
    this.getCurrentClass(this.$route.params.id)
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
          text: 'Proctored at',
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
    }
  }
}
</script>
