<template>
    <div class="">
      <ValidationObserver ref="choice_validator_observer">
        <v-row>
          <v-col cols="8" lg="7" sm="12" md="12">
            <ValidationProvider name="choice" rules="required" v-slot="{ errors }">
              <v-text-field
                v-model="choice.value"
                label="Choice"
                :error-messages="errors"
                outlined>
              </v-text-field>
            </ValidationProvider>
          </v-col>
          <v-col cols="2" lg="2" sm="12" md="12">
            <ValidationProvider name="weight" vid="weight" rules="min_value:0|max_value:1" v-slot="{ errors }">
              <v-text-field
                v-model="choice.weight"
                label="Weight"
                type="number"
                :error-messages="errors"
                outlined >
              </v-text-field>
            </ValidationProvider>
          </v-col>
          <v-col cols="3" lg="3" sm="12" md="12">
            <ValidationProvider name="correct_choice" rules="required_if:weight,1" v-slot="{ errors }">
              <v-checkbox
                label="Correct Choice"
                v-model="choice.is_correct_choice"
                :error-messages="errors"
                :value="false">
              </v-checkbox>
            </ValidationProvider>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12" lg="12" sm="12" md="12">
            <ValidationProvider name="feedback" rules="required" v-slot="{ errors }">
              <vue-editor v-model="choice.feedback" :editorToolbar="toolbar"></vue-editor>
              <span v-show="hasFeedbackError(errors)" class="red--text text--darken-1 font-weight-light">This field is required</span>
            </ValidationProvider>
          </v-col>
        </v-row>
      </ValidationObserver>
    </div>
</template>

<script>

import {
  ValidationObserver,
  ValidationProvider
} from 'vee-validate'

import { VueEditor } from 'vue2-editor'

export default {
  name: 'QuestionsChoices',
  components: {
    ValidationObserver,
    ValidationProvider,
    VueEditor
  },
  props: {
    choice: {
      type: Object,
      default: {}
    }
  },
  data: function () {
    return this.init()
  },
  methods: {
    init () {
      return {
        toolbar: [
          [{ header: [1, 2, false] }],
          ['bold', 'italic', 'underline'],
          ['code-block', 'link']
        ],
        editors: [],
        choiceCount: 0
      }
    },
    hasFeedbackError (errorObj) {
      return errorObj &&
        !this._.isEmpty(errorObj)
    }
  }
}
</script>
