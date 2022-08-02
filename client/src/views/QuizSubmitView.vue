<template>
  <v-container fluid> </v-container>
</template>

<script>
export default {
  name: 'QuizSubmitView',
  computed: {
    quiz_uuid: function () {
      return this.$route.params.uuid
    }
  }
}
</script>
