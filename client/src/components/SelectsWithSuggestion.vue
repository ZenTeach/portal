<template>
  <v-container fluid>
    <v-select
      v-model="selectedFruits"
      :items="data"
      label="Favorite Fruits"
      v-bind="$attrs"
      v-on="$listeners"
      solo
      outlined
    >
      <!-- Suggestion sub block-->
      <template v-slot:prepend-item>
        <v-list-item>
          <v-list-item-content>
            <v-list-item-title>
              ✨ Suggested
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-divider class="mt-2"></v-divider>
      </template>
      <template v-slot:item="{ item }">
        <span v-if="item.suggested">
          <p class="font-weight-black">
            {{ item.text }} <br/>
          </p>
        </span>
        <span v-else>
        </span>
          <p class="">
            {{ item.text }}
          </p>
      </template>
      <!-- <template v-slot:append-item>
        <v-divider class="mb-2"></v-divider>
        <v-list-item disabled>
          <v-list-item-avatar color="grey lighten-3">
            <v-icon>
              mdi-food-apple
            </v-icon>
          </v-list-item-avatar>

          <v-list-item-content v-if="likesAllFruit">
            <v-list-item-title>
              Holy smokes, someone call the fruit police!
            </v-list-item-title>
          </v-list-item-content>

          <v-list-item-content v-else-if="likesSomeFruit">
            <v-list-item-title>
              Fruit Count
            </v-list-item-title>
            <v-list-item-subtitle>
              {{ selectedFruits.length }}
            </v-list-item-subtitle>
          </v-list-item-content>

          <v-list-item-content v-else>
            <v-list-item-title>
              How could you not like fruit?
            </v-list-item-title>
            <v-list-item-subtitle>
              Go ahead, make a selection above!
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
      </template> -->
    </v-select>
  </v-container>
</template>

<script>
  export default {
    name: "SelectsWithSuggestion",
    props: {

    },
    data: () => ({
      data: [
        { value: 'eduqas', text: 'Eduqas', suggested: true },
        { value: 'aqa', text: 'AQA', suggested: false },
        { value: 'ocr_gateway', text: 'OCR Gateway', suggested: false },
        { value: 'edexcel', text: 'EdExcel', suggested: false },
        { value: 'ocr_new', text: 'OCR 21st Century', suggested: false },
        { value: 'wjec', text: 'WJEC', suggested: false },
        { value: 'ccea', text: 'CCEA', suggested: false }
      ],
      selectedFruits: [],
    }),

    computed: {
    },
    mounted: function () {
      // enhance examboard
      // let teacher_classes = 
    },
    methods: {
    },
  }
</script>
