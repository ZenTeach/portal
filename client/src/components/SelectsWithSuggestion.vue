<template>
  <v-select
    v-model="dataModel"
    @keyup="$emit('update:dataModel', dataModel)"
    :items="items"
    :label="label"
    v-bind="$attrs"
    v-on="$listeners"
  >
    <template v-slot:no-data>
      <p class="mx-3 my-3">
        Please select a subject first.
      </p>
    </template>
    <template v-slot:prepend-item>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title class="text-overline text--secondary">
            <h3>
              ✨ Suggested
            </h3>
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
      <v-divider class="mt-2"></v-divider>
    </template>
    <template v-slot:item="{ item }">
      <span v-if="item.suggested">
        <p class="font-weight-black m-3">
          {{ item.text }} <br/>
        </p>
      </span>
      <span v-else>
        <p class="">
          {{ item.text }}
        </p>
      </span>
    </template>
  </v-select>
</template>

<script>
export default {
  name: 'SelectsWithSuggestion',
  props: {
    items: {
      type: Array,
      default: []
    },
    dataModel: {
      type: String,
      default: '',
      required: true
    },
    label: {
      type: String,
      default: ''
    }
  }
}
</script>
