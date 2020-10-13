<template>
  <v-container fluid>
    <v-flex xs12 sm12 md12 lg12>
      <v-row>
        <v-col>
          <v-card>
            <v-card-text>
              <p>Classrooms</p>
            </v-card-text>
            <div>
              <v-data-table
                :headers="headers"
                :items="classList"
                :items-per-page="5"
                class="elevation-1"
                hide-default-footer
              >
                <template v-slot:item.name="props">
                  <a :href="'/classroom/' + props.item.uuid">{{ props.item.name }}</a>
                </template>
                <template v-slot:item.actions="{ item }">
                  <v-icon
                    large
                    @click="deleteItem(item)"
                  >
                    mdi-trash-can-outline
                  </v-icon>
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

const { mapGetters, mapActions } = createNamespacedHelpers('classrooms')
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
          text: 'Class',
          align: 'left',
          sortable: false,
          value: 'name'
        },
        { text: 'Subject', sortable: true, value: 'subject' },
        { text: 'Starts', sortable: false, value: 'start_date' },
        { text: '', sortable: false, value: 'actions' }
      ],
      subjects: ['Physics', 'Chemistry', 'Biology'],
      dialog: false,
      start_date: new Date().toISOString().substr(0, 10),
      menu: false,
      classname: '',
      subject: ''
    }
  },
  mounted: function () {
    this.fetchClasses()
  },
  computed: {
    ...mapGetters({
      classList: 'CLASSLIST'
    })
  },
  methods: {
    ...mapActions({
      fetchClasses: 'GETCLASSES',
      createClass: 'CREATECLASS',
      deleteClass: 'DELETECLASSROOM'
    }),
    close () {
      this.dialog = false
      setTimeout(() => {
        this.editedItem = Object.assign({}, this.defaultItem)
        this.editedIndex = -1
      }, 300)
    },
    addClass () {
      const payload = {
        name: this.classname,
        subject: this.subject,
        start_data: this.start_date
      }

      this.createClass(payload)
      this.close()
    },
    deleteItem (item) {
      this.deleteClass(item.id)
    }
  }
}
</script>
