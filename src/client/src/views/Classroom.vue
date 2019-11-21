<template>
  <v-container>
    <v-layout row column wrap justify-center>
      <v-flex sm-8 md-5 lg-3 class="ma-6">
				<v-col cols="12" lg="4">
				<material-chart-card
          :data="emailsSubscriptionChart.data"
          :options="emailsSubscriptionChart.options"
          :responsive-options="emailsSubscriptionChart.responsiveOptions"
          color="blue"
          type="Bar"
        >
          <h4 class="title font-weight-light">
            Class Grade Distribution
          </h4>
          <p class="category d-inline-flex font-weight-light">
            Median Grade
          </p>

          <template v-slot:actions>
            <v-icon
              class="mr-2"
              small
            >
              mdi-clock-outline
            </v-icon>
            <span class="caption grey--text font-weight-light">updated 10 minutes ago</span>
          </template>
        </material-chart-card>
				</v-col>
			</v-flex>

      <v-flex sm-8 md-10 lg-10 class="ma-6">
        <v-data-table
          :headers="headers"
          :items="current_class.quizzes"
          :items-per-page="3"
          class="elevation-1"
          hide-default-footer >
          <template v-slot:item.name="props">
            <a @click.native.stop.prevent="openQuiz(props.item.id)">Quiz {{ props.item.name }}</a>
          </template>
          <template v-slot:item.status="{ item }">
            <v-chip :color="statusToColor[item.status]">{{ item.status }}</v-chip>
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
import MaterialChartCard from '@/components/ChartCard';
import StudentList from '@/components/StudentList';
import QuizCreator from '@/components/QuizCreator';
import { createNamespacedHelpers } from 'vuex';
import { fetchQuizPDF } from '@/service/classrooms';
const { mapState } = createNamespacedHelpers("classrooms");

export default {
	name: "Classroom",
	components: {
		MaterialChartCard,
		StudentList,
		QuizCreator
	},
	mounted(){
		this.$store.dispatch("classrooms/GETCURRENTCLASS", this.$route.params.id, { root: true });
	},
	computed: {
		...mapState(["current_class"])
	},
  data() {
    return {
      headers: [
        {
          text: "Quiz",
          align: "left",
          sortable: false,
          value: "name"
        },
        {
          text: "Status",
          sortable: false,
          value: "status"
        },
        {
          text: "Proctored at",
          value: "held_on"
        }
      ],
      quizzes: [],
			dialog: false,
      statusToColor: {
        created: "yellow",
        administered: "green",
        cancelled: "red"
      },
			emailsSubscriptionChart: {
				data: {
					labels: ['Quiz 1', 'Quiz 2', 'Quiz 3' ],
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
			},
		};
	},
  methods: {
		closeQuizCreatorDialog() {
			this.dialog = false;
			this.$store.commit("app/RESET_QUESTION_SEARCH", {}, {root: true});
		},

		openQuiz(quiz_id) {
			fetchQuizPDF(quiz_id).then(response => {
				var fileURL = window.URL.createObjectURL(new Blob([response.data]));
				var fileLink = document.createElement('a');

				fileLink.href = fileURL;
				fileLink.setAttribute('download', 'file.pdf');
				document.body.appendChild(fileLink);

				fileLink.click();
				fileLink.remove();
			})
		}
	}
};
</script>
