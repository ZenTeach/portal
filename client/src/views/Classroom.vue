<template>
  <v-container>
    <v-layout row column wrap justify-center v-if="$route.name == 'Classroom'">
      <v-flex sm-8 md-10 lg-10 class="ma-6">
        <span>
          <p class="text-lg-h4 text-sm-h6 font-weight-normal text-body-1">{{ current_class.name }}</p>
          </span>

        <v-card>
          <v-card-title>
            <p class="text-lg-h6 text-sm-body-2 font-weight-normal text-caption">My Quizzes</p>
            <v-spacer></v-spacer>
            <v-text-field
                v-model="search"
                append-icon="mdi-magnify"
                label="Search"
                single-line
                hide-details
              ></v-text-field>
            </v-card-title>
            <v-data-table
              :headers="headers"
              :items="current_class.quizzes"
              :items-per-page="10"
              class="elevation-1"
              :search="search"
              sort-by="created"
              sort-desc="false"
              :footer-props="footerProps">
                <template v-slot:item.name="props">
                  <div class="d-flex justify-left">
                    <span>
                      <a :href="'/quiz/' +  props.item.uuid" class="d-inline-block mx-1 text-body-1">
                        <!-- <v-icon medium color="primary" elevation="12">mdi-open-in-app</v-icon> -->
                        {{ props.item.name }}
                      </a>
                    </span>
                    <v-edit-dialog
                      :return-value.sync="props.item.name"
                      class="d-inline-block quiz_name_editor"
                      @save="save(props.item.name, props.item.uuid)"
                      @cancel="cancel"
                      @open="open"
                      @close="close">
                      <v-icon small color="secondary" ref="quiz_name_edit" elevation="12">mdi-pencil-circle-outline</v-icon>
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
                    <span class="mx-3">
                      <v-chip v-if="props.item.private" small>Private</v-chip>
                      <v-chip v-else small>Public</v-chip>
                    </span>
                  </div>
                </template>
                <template v-slot:item.status="{ item }">
                  <v-chip :color="statusToColor[item.status]">{{ item.status }}</v-chip>
                </template>
                <template v-slot:item.created="{item}">
                  <p>
                    {{ item.created | formatDate }}
                  </p>
                </template>
                <template v-slot:item.url="{ item }">
                  <v-btn text text elevation="0" class="d-inline-block mx-1" @click="copytoClipboard(item)">
                      <v-icon small color="primary" elevation="12">mdi-content-copy</v-icon>
                      <span class="text-caption m-0 blue--text">Copy Quiz Link</span>
                    </v-btn>
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
        </v-card>
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
import Api from '@/service/Api'

const { mapGetters, mapActions } = createNamespacedHelpers('classrooms')

export default {
  name: 'Classroom',
  components: {
    MaterialChartCard,
    StudentList,
    QuizCreator
  },
  mounted () {
    if (this.$route.name === 'Classroom') {
      this.getClassroom(this.$route.params.id)
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
      search: '',
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
      footerProps: {
        showFirstLastPage: true,
        firstIcon: 'mdi-arrow-collapse-left',
        lastIcon: 'mdi-arrow-collapse-right',
        prevIcon: 'mdi-minus',
        nextIcon: 'mdi-plus'
      },
      headers: [
        {
          text: 'Quiz',
          align: 'left',
          value: 'name'
        },
        {
          text: '', // actions
          value: 'url'
        },
        {
          text: 'Status',
          value: 'status'
        },
        // TODO: Use actual proctored date
        {
          text: 'Created',
          value: 'created'
        }
      ],
      quizzes: [],
      dialog: false,
      statusToColor: {
        created: 'yellow',
        administered: 'green',
        cancelled: 'red'
      }
    }
  },
  methods: {
    ...mapActions({
      getClassroom: 'GETCURRENTCLASS'
    }),
    closeQuizCreatorDialog () {
      this.dialog = false
      this.getClassroom(this.$route.params.id)
    },
    copytoClipboard (item) {
      navigator.clipboard.writeText(item.url)
    },
    save (name, uuid) {
      this.snack = true
      this.snackColor = 'success'
      this.snackText = 'Data saved'
      Api.patch(`/class_quiz/${uuid}`,
        {
          name: name
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
    showQuizNameEditor () {
      this.$refs.quiz_name_edit.classList.toggle('visible')
    },
    close () {
    }
  }
}
</script>

<style scoped>
.quiz_name_edit_btn {
  visibility: hidden;
}
.quiz_name_edit_btn:hover {
  visibility: visible;
}
</style>
