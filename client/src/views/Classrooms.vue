<template>
  <v-container fluid>
    <v-flex xs12 sm12 md12 lg12>
      <v-row>
        <v-col>
          <v-card>
            <v-card-text v-if="!isMobile">
              <p>Classrooms</p>
            </v-card-text>
            <div>
              <v-data-table
                :headers="headers"
                :items="classList"
                :items-per-page="5"
                class="elevation-1"
              >
                <template v-slot:item.valid="props">
                  <v-tooltip left>
                    <template v-slot:activator="{ on, attrs }">
                      <v-icon
                        v-if="has_empty_examboard(props.item)"
                        color="red"
                        size="24"
                        v-bind="attrs"
                        v-on="on">
                        mdi-alert
                      </v-icon>
                    </template>
                    <span>Please select an exam board.</span>
                  </v-tooltip>
                </template>
                <template v-slot:item.name="props">
                  <div class="d-flex flex-column">
                    <a :href="'/classroom/' + props.item.id" class="text-body-1">{{ props.item.name }}</a>
                  </div>
                </template>
                <template v-slot:item.key_stage="{ item }">
                    <small class="grey lighten-4 black--text text-center text-caption" style="width:70%;">
                      {{ item.key_stage }}
                      <v-tooltip left>
                        <template v-slot:activator="{ on, attrs }">
                        <v-icon
                          size="12"
                          v-bind="attrs"
                          v-on="on">
                          mdi-information-outline
                        </v-icon>
                        </template>
                        <span>Key stages signify levels.</span>
                      </v-tooltip>
                    </small>
                </template>
                <template v-slot:item.actions="{ item }">
                  <v-icon
                    medium
                    class="m-2"
                    @click="deleteItem(item)"
                  >
                    mdi-trash-can-outline
                  </v-icon>
                  <v-icon medium class="m-2" @click="editItem(item)">
                    mdi-pencil
                  </v-icon>
                </template>
                <template v-slot:item.start_date="{ item }">
                    {{ item.start_date | formatDate }}
                </template>
                <template v-slot:item.exam_board="{ item }">
                  {{ item.exam_board | formatExamBoard }}
                </template>
                <template v-slot:footer>
                  <v-dialog v-model="dialog" max-width="500px" max-height="450px">
                    <template v-slot:activator="{ on }">
                      <v-btn color="primary" right fab dark class="ma-2 pa-2" v-on="on">
                        <v-icon>mdi-plus</v-icon>
                      </v-btn>
                    </template>

                    <ValidationObserver ref="observer" v-slot="{ invalid, validated, passes }">
                    <v-card>
                      <v-card-title>
                        <span class="headline">Add a new class</span>
                      </v-card-title>

                      <v-card-text>
                        <v-container>
                          <v-row>
                            <v-col cols="10" lg="12" sm="9" md="12">
                              <ValidationProvider rules="required" name="classname">
                              <v-text-field label="Class name" v-model="classname" outlined grow></v-text-field>
                              </ValidationProvider>

                              <ValidationProvider rules="required" name="subject">
                              <v-select :items="subjects" label="Subject" v-model="subject" outlined></v-select>
                              </ValidationProvider>

                              <ValidationProvider rules="required" name="Year group">
                              <v-select :items="yearGroupSelection" label="Year Group" v-model="yearGroup" outlined></v-select>
                              </ValidationProvider>

                              <ValidationProvider rules="required" name="Exam Board">
                                <v-select :items="examBoardSelection" label="Exam Board" v-model="examBoard" outlined></v-select>
                              </ValidationProvider>

                              <v-menu
                                ref="menu"
                                v-model="menu"
                                :close-on-content-click="false"
                                :return-value.sync="start_date"
                                transition="scale-transition"
                                offset-y
                                min-width="290px"
                              >
                                <template v-slot:activator="{ on }">
                                  <ValidationProvider rules="required" name="Start date" v-slot="{ errors }">
                                  <v-text-field
                                    v-model="start_date"
                                    label="Start date"
                                    :error-messages="errors"
                                    prepend-icon="event"
                                    readonly
                                    v-on="on"
                                    outlined
                                  ></v-text-field>
                                  </ValidationProvider>
                                </template>
                                <v-date-picker v-model="start_date" no-title scrollable>
                                  <div class="flex-grow-1"></div>
                                  <v-btn text color="primary" @click="menu = false">Cancel</v-btn>
                                  <v-btn
                                    text
                                    color="primary"
                                    @click="$refs.menu.save(start_date)"
                                  >OK</v-btn>
                                </v-date-picker>
                              </v-menu>
                            </v-col>
                          </v-row>
                        </v-container>
                      </v-card-text>

                      <v-card-actions>
                        <div class="flex-grow-1"></div>
                        <v-btn color="blue darken-1" text @click="close" outlined>Cancel</v-btn>
                        <v-btn color="blue darken-1" text outlined :disabled="invalid || !validated" @click="passes(addClass)">Save</v-btn>
                      </v-card-actions>
                    </v-card>
                    </ValidationObserver>
                  </v-dialog>
                </template>
              </v-data-table>
              <v-dialog v-model="editDialog" max-width="600px" max-height="auto">
                <ValidationObserver ref="edit_observer" v-slot="{ passes }">
                  <v-card>
                    <v-card-title primary-title>
                      Edit class
                    </v-card-title>
                    <v-card-text>
                      <v-container fluid>
                        <v-row no-gutters>
                          <v-col cols="12" lg="12" sm="12" md="12">
                            <ValidationProvider rules="required" name="classname">
                              <v-text-field label="Class name" v-model="editedItem.name" outlined></v-text-field>
                            </ValidationProvider>

                            <ValidationProvider rules="required" name="subject">
                              <v-select :items="subjects" label="Subject" :placeholder="editedItem.subject.name" v-model="editedItem.subject" outlined></v-select>
                            </ValidationProvider>

                            <ValidationProvider rules="required" name="year_group">
                              <v-select :items="yearGroupSelection" label="Year Group" v-model="editedItem.year_group" outlined></v-select>
                            </ValidationProvider>
                            <ValidationProvider rules="required" name="exam_board">
                              <v-select :items="examBoardSelection" label="Exam Board" v-model="editedItem.exam_board" outlined></v-select>
                            </ValidationProvider>
                            <ValidationProvider name="Start date">
                              <v-text-field
                                v-model="start_date"
                                label="Start date"
                                prepend-icon="event"
                                disabled
                                readonly
                                outlined
                              ></v-text-field>
                            </ValidationProvider>
                          </v-col>
                        </v-row>
                      </v-container>
                    </v-card-text>
                    <v-card-actions>
                        <div class="flex-grow-1"></div>
                        <v-btn color="blue darken-1" text @click="close" outlined>Cancel</v-btn>
                        <v-btn color="blue darken-1" text outlined :disabled="!passes" @click="updateClass">Update</v-btn>
                      </v-card-actions>
                  </v-card>
                </ValidationObserver>
              </v-dialog>
            </div>
          </v-card>
        </v-col>
      </v-row>
    </v-flex>
  </v-container>
</template>

<script>
import { createNamespacedHelpers } from 'vuex'
import {
  ValidationObserver,
  ValidationProvider
} from 'vee-validate'
import moment from 'moment'

const { mapGetters, mapActions } = createNamespacedHelpers('classrooms')
const { mapGetters: appGetters } = createNamespacedHelpers('app')
export default {
  name: 'Classrooms',
  components: {
    ValidationObserver,
    ValidationProvider
  },
  data () {
    return {
      headers: [
        {
          text: '',
          align: 'left',
          sortable: false,
          value: 'valid'
        },
        {
          text: 'Class',
          align: 'left',
          sortable: false,
          value: 'name'
        },
        { text: 'Subject', sortable: true, value: 'subject.name' },
        { text: 'Starts', sortable: false, value: 'start_date' },
        { text: 'Exam Board', sortable: true, value: 'exam_board' },
        { text: 'Key Stage', sortable: true, value: 'key_stage' },
        { text: '', sortable: false, value: 'actions' }
      ],
      subjects: ['Physics', 'Chemistry', 'Biology'],
      yearGroupSelection: ['Year 7', 'Year 8', 'Year 9', 'Year 10', 'Year 11', 'Year 12', 'Year 13'],
      examBoard: '',
      examBoardSelection: [
        { value: 'aqa', text: 'AQA' },
        { value: 'ocr_gateway', text: 'OCR Gateway' },
        { value: 'edexcel', text: 'EdExcel' },
        { value: 'ocr_new', text: 'OCR 21st Century' },
        { value: 'wjec', text: 'WJEC' },
        { value: 'ccea', text: 'CCEA' },
        { value: 'eduqas', text: 'Eduqas' }
      ],
      yearGroup: '',
      dialog: false,
      editDialog: false,
      start_date: new Date().toISOString().substr(0, 10),
      menu: false,
      classname: '',
      subject: [],
      editedItem: {}
    }
  },
  filters: {
    formatExamBoard: function (value) {
      if (!value) return ''

      const defaultExamBoard = [
        { value: 'aqa', text: 'AQA' },
        { value: 'ocr_gateway', text: 'OCR Gateway' },
        { value: 'edexcel', text: 'EdExcel' },
        { value: 'ocr_new', text: 'OCR 21st Century' },
        { value: 'wjec', text: 'WJEC' },
        { value: 'ccea', text: 'CCEA' },
        { value: 'eduqas', text: 'Eduqas' }
      ]

      const examBoard = defaultExamBoard.filter((val) => value === val.value)
      return examBoard[0].text
    },
    formatDate: function (value) {
      if (!value) return ''
      if (value) {
        return moment(String(value)).format('DD/MM/YYYY')
      }
    }
  },
  mounted: function () {
    this.fetchClasses()
    this.subjects = this.getSubjects
      .filter(x => x.enabled)
      .map(x => x.name)
  },
  watch: {
    subjects: function (val) {
      this.getSubjects
        .filter(x => x.enabled)
        .map(x => x.name)
        .sort()
    }
  },
  computed: {
    ...mapGetters({
      classList: 'CLASSLIST'
    }),
    ...appGetters({
      getSubjects: 'getSubjects'
    })
  },
  methods: {
    ...mapActions({
      fetchClasses: 'GETCLASSES',
      createClass: 'CREATECLASS',
      deleteClass: 'DELETECLASSROOM',
      updateClassroom: 'UPDATECLASSROOM'
    }),
    isMobile: function () {
      return ['md', 'sm', 'xs'].includes(this.$vuetify.breakpoint.name)
    },
    close () {
      this.dialog = false
      setTimeout(() => {
        this.editedItem = Object.assign({}, this.defaultItem)
        this.editedIndex = -1
        this.editDialog = false
      }, 100)
    },
    addClass () {
      const payload = {
        name: this.classname,
        subject: this.subject,
        exam_board: this.examBoard,
        start_data: this.start_date,
        year_group: this.yearGroup
      }

      this.createClass(payload)
      this.close()
    },
    deleteItem (item) {
      this.deleteClass(item.id)
    },
    has_empty_examboard (item) {
      return (item.exam_board === '' || item.exam_board === null || item.exam_board === undefined)
    },
    editItem (item) {
      this.editedItem = {
        id: item.id,
        exam_board: item.exam_board,
        name: item.name,
        subject: item.subject.name,
        year_group: item.year_group
      }
      this.editDialog = true
    },
    updateClass () {
      this.updateClassroom(this.editedItem)
      this.close()
    }
  }
}
</script>
