<template>
	<div>
		<v-text-field
            label="SearchInput"
            placeholder="Question.."
			@click:append="searchEventListener"
			v-model="searchInput"
			append-icon="search"
            solo
        ></v-text-field>
	</div>
</template>
<script>

export default {
  name: 'QuestionSearch',
  props: {
    subject: String,
    topic: String,
    knowledge_items: Array
  },
  data () {
    return {
      searchInput: ''
    }
  },
  methods: {
    searchEventListener () {
      this.$store.dispatch('app/QUERY_QUESTIONS', {
        query: this.searchInput,
        subject: this.subject,
        topic: this.topic,
        knowledge_item: this.knowledge_items
      }, { root: true })

      this.$emit('update:searchResult', true)
    }
  }
}
</script>
