<template>
    <v-autocomplete
        @keyup.capture="searchForTopicListener"
        clearable
        :loading="loading"
        single-line
        :success="searchSuccess"
        :error="searchError"
        :search-input.sync="search"
        :menu-props="{auto: true, overflowY: true}"
        v-bind="$attrs"
        return-object
        v-on="$listeners">
        <!-- Populate results after search -->
        <!-- Loading state -->
        <template v-slot:no-data>
            <!-- Check if loading, then show loading bar -->
            <!-- Show create action -->
            <!-- TODO: Check why autocomplete is in error state post-create action -->
            <p class="mx-4 my-2 text-caption">Topic not found. <a class="black--text text-decoration-underline" @click="createTopic">Click to save this topic?</a></p>
        </template>
        <!-- Show create action result -->
        <!-- Scheduled save -->
    </v-autocomplete>
</template>

<script>

import { createNamespacedHelpers } from 'vuex'

const { mapActions } = createNamespacedHelpers('app')

export default {
  name: 'SelectWithAjax',
  data () {
    return {
      topics: [],
      options: [],
      loading: false,
      value: null,
      search: '',
      topicCreate: false,
      searchSuccess: false,
      searchError: false,
      searchTimeout: null,
      searchDelay: 1500,
      apiDebounce: null
    }
  },
  props: {
    selectedTopic: {
      type: String,
      default: ''
    },
    subject: {
      type: String,
      required: true
    }
  },
  methods: {
    ...mapActions({
      searchTopics: 'SEARCH_TOPICS',
      createTopicAction: 'CREATE_TOPIC'
    }),
    searchForTopicListener () {
      if (!this.apiDebounce) {
        this.apiDebounce = this._.debounce(this.searchForTopic, this.searchDelay, {
          leading: true
        })
      }
      return this.apiDebounce()
    },
    createTopic () {
      const payload = {
        value: this.search,
        subject: this.subject
      }
      console.log('Created topic with, ', payload)
      if (this.apiDebounce) {
        this.apiDebounce.cancel()
      }

      this.createTopicAction(payload)
        .then(() => {
          this.searchSuccess = true
          setTimeout(function () {
            this.searchSuccess = false
          }, 2000)
        }).catch((err) => {
          console.log('Error creating topic', err)
          this.searchError = true
        })
    },
    searchForTopic () {
      if (this.search === '' || this.search === null) { return }
      this.loading = true
      this.searchTopics({
        search: this.search
      }).then(() => {
        this.loading = false
        this.searchSuccess = true
      }).catch(function (error) {
        console.error(error)
        this.loading = false
        this.searchError = true
      })
    }
  }
}
</script>

<style>

</style>
