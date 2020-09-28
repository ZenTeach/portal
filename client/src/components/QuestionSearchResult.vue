<template>
  <v-list two-line subheader flat>
    <v-list-item-group multiple>
      <template v-for="item in resultSet" >
        <v-list-group
          sub-group
          value="false"
          :key="item.question.uuid">
          <template v-slot:activator>
            <v-list-item>
              <template v-slot:default="{active, toggle}">
                <v-list-item-action>
                  <v-checkbox
                      :ripple="false"
                      color="primary"
                      class="ma-2"
                      @click.stop="active ? removeFromSelectedQuestions(item, toggle) : addToSelectedQuestions(item, toggle)"
                    ></v-checkbox>
                </v-list-item-action>

                <v-list-item-content>
                  <v-edit-dialog
                    :return-value.sync="item.question"
                    @save="save()"
                    ref="questionEditBox">
                  {{ item.question }}
                    <template v-slot:input>
                      <v-text-field
                        v-model="item.question"
                        :rules="[max200chars]"
                        label="Edit"
                        single-line
                        counter
                      ></v-text-field>
                    </template>
                  </v-edit-dialog>

                  <v-list-item-subtitle v-text="questionTypeMapping(item.question_type)"></v-list-item-subtitle>
                </v-list-item-content>
              </template>
            </v-list-item>
          </template>
          <v-list-item v-for="(choice, index) in item.choices" :key="index + 1">
            <v-list-item-content v-text="choice.value"></v-list-item-content>
          </v-list-item>
        </v-list-group>
      </template>
    </v-list-item-group>
  </v-list>
</template>

<script>
export default {
  name: 'QuestionSearchResult',
  props: {
    resultSet: Array
  },
  computed: {},
  data () {
    return {
      selectedQuestions: [],
      isChoiceDisplayed: false,
      max200chars: v => v.length <= 200 || 'Input too long!'
    }
  },
  methods: {
    questionTypeMapping (type) {
      const types = {
        1: 'Multiple Choice',
        2: 'Short Answer',
        3: 'Long Answer'
      }
      return types[type]
    },
    debug (item) {
    },
    addToSelectedQuestions (item, cb) {
      this.$store.commit('app/ADD_SELECTED_QUESTIONS', item, { root: true })
      cb()
    },
    removeFromSelectedQuestions (item, cb) {
      this.$store.commit('app/REMOVE_SELECTED_QUESTIONS', item, { root: true })
      cb()
    },
    save () {}
  }
}
</script>
