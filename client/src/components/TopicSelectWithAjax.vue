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
        v-on="$listeners">
        <template v-slot:no-data>
            <p class="mx-4 my-2 text-caption">Topic not found. <a class="black--text text-decoration-underline" @click="createTopic">Click to save this topic?</a></p>
        </template>
    </v-autocomplete>
</template>

<script>

import { createNamespacedHelpers } from 'vuex'

const { mapActions } = createNamespacedHelpers('app')

export default {
  name: 'TopicSelectWithAjax',
  data () {
    return {
      loading: false,
      search: '',
      searchSuccess: false,
      searchError: false,
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
      if (this.apiDebounce) {
        this.apiDebounce.cancel()
      }

      this.createTopicAction(payload)
        .then(() => {
          this.searchSuccess = true
          setTimeout(function () {
            this.searchSuccess = false
          }, 2000)
        }).catch(() => {
          this.searchError = true
        })
    },
    searchForTopic () {
      if (this.search === '' || this.search === null) { return }
      this.loading = true
      this.searchTopics({
        search: this.search,
        subject: this.subject
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
