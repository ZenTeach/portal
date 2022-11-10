<template>
  <v-list two-line subheader text v-bind="$attrs">
    <v-list-item-group multiple v-if="hasResult(resultSet)">
      <template v-for="item in resultSet" >
        <v-list-group
          sub-group
          :ripple="false"
          :value="false"
          :key="item.id">
          <template v-slot:activator>
            <v-list-item class="d-flex align-baseline">
              <template v-slot:default="{active, toggle}">
                <v-list-item-action v-if="selectable">
                  <v-checkbox
                      :ripple="false"
                      color="primary"
                      class="ma-lg-2"
                      :input-value.sync="item.isSelected"
                      value
                      @click.stop="active ? addToSelectedQuestions(item, toggle) : removeFromSelectedQuestions(item, toggle)"
                    ></v-checkbox>
                </v-list-item-action>

                <v-list-item-content class="d-flex justify-space-between">
                  <v-row>
                    <v-col cols="6" class="my-5">
                      <h3>{{item.question}}</h3>
                      <v-list-item-subtitle v-text="questionTypeMapping(item.question_type)"></v-list-item-subtitle>
                      <v-spacer></v-spacer>
                      <div v-if="showLabels">
                        <v-chip color="green lighten-5" class="mx-lg-1" small>
                          <v-tooltip bottom>
                            <template v-slot:activator="{ on, attrs }">
                              <p
                                  style="max-width: 16ch;"
                                  v-bind="attrs"
                                  v-on="on"
                                  class="text-caption text-truncate font-weight-bold pt-4">{{item.topic.value}}</p>
                            </template>
                            <p>{{item.topic.value}}</p>
                          </v-tooltip>
                        </v-chip>
                        <v-chip color="pink lighten-5" class="mx-1" small>
                          <v-tooltip bottom>
                            <template v-slot:activator="{ on, attrs }">
                              <p style="max-width: 32ch;"
                                  v-bind="attrs"
                                  v-on="on"
                                  class="text-caption text-truncate font-weight-bold pt-4">{{item.knowledge_item.value}}</p>
                            </template>
                            <p>{{item.knowledge_item.value}}</p>
                          </v-tooltip>
                        </v-chip>
                      </div>
                    </v-col>
                    <v-col cols="4" v-if="show_user_created_badge">
                      <v-list-item-icon v-if="item.user_created">
                        <v-chip color="primary" small>User Created</v-chip>
                      </v-list-item-icon>
                    </v-col>
                    <v-col cols="2" class="text-center">
                      <slot name="extra_actions" v-bind:item="item"></slot>
                    </v-col>
                  </v-row>
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
    <v-list-item v-else>
      <h2> {{ no_data_text }}</h2>
    </v-list-item>
  </v-list>
</template>

<script>
import { createNamespacedHelpers } from 'vuex'

const { mapMutations } = createNamespacedHelpers('app')
export default {
  name: 'QuestionSearchResult',
  props: {
    resultSet: {
      type: Array,
      default: []
    },
    selectable: {
      type: Boolean,
      default: true
    },
    show_user_created_badge: {
      type: Boolean,
      default: true
    },
    showLabels: {
      type: Boolean,
      default: true
    },
    no_data_text: {
      type: String,
      default: 'No Question found!'
    }
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
    ...mapMutations({
      addSelectedQuestions: 'ADD_SELECTED_QUESTIONS',
      removeSelectedQuestions: 'REMOVE_SELECTED_QUESTIONS'
    }),
    questionTypeMapping (type) {
      const types = {
        1: 'Multiple Choice',
        2: 'Short Answer',
        3: 'Long Answer'
      }
      return types[type]
    },
    hasResult (result) {
      return result.length > 0
    },
    addToSelectedQuestions (item, cb) {
      this.addSelectedQuestions(item)
      cb()
    },
    removeFromSelectedQuestions (item, cb) {
      this.removeSelectedQuestions(item)
      cb()
    }
  }
}
</script>
