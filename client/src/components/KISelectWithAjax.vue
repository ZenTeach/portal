<template>
    <v-autocomplete
        @keyup.capture="searchForKIListener"
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
            <p class="mx-4 my-2 text-caption">Knowledge Item not found. <a class="black--text text-decoration-underline" @click="createKI">Click to save this knowledge item?</a></p>
        </template>
    </v-autocomplete>
</template>

<script>

import { createNamespacedHelpers } from 'vuex'

const { mapActions } = createNamespacedHelpers('app')

export default {
  name: 'KiSelectWithAjax',
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
      required: true
    },
    subject: {
      type: String,
      required: true
    }
  },
  methods: {
    ...mapActions({
      searchKnowledgeItems: 'SEARCH_KNOWLEDGE_ITEMS',
      createKIAction: 'CREATE_KNOWLEDGE_ITEM'
    }),
    searchForKIListener () {
      if (!this.apiDebounce) {
        this.apiDebounce = this._.debounce(this.searchForKnowledgeItems, this.searchDelay, {
          leading: true
        })
      }
      return this.apiDebounce()
    },
    createKI () {
      const payload = {
        value: this.search,
        subject: this.subject,
        topic: this.selectedTopic
      }
      if (this.apiDebounce) {
        this.apiDebounce.cancel()
      }

      this.createKIAction(payload)
        .then(() => {
          this.searchSuccess = true
          setTimeout(function () {
            this.searchSuccess = false
          }, 2000)
        }).catch(() => {
          this.searchError = true
        })
    },
    searchForKnowledgeItems () {
      if (this.search === '' || this.search === null) { return }
      this.loading = true
      this.searchKnowledgeItems({
        search: this.search,
        subject: this.subject,
        topic: this.selectedTopic
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
