<template>
    <v-main>
        <v-container fluid fill-height>
            <v-layout row justify-center class="align-self-center">
                <v-row v-if="loading" no-gutters class="flex-column white lighten-4 justify-center pby-6">
                    <v-skeleton-loader :loading="loading" type="image,card" class="white">
                    </v-skeleton-loader>
                </v-row>
                <v-row v-if="!loading" no-gutters class="flex-column white lighten-4 justify-center pby-6">
                    <v-img src="../assets/Join.png" height="350" class="white lighten-4 background_image" aspect-ratio="2.5" contain></v-img>
                    <h3 class="subheading foreground_text text-center">Account confirmation succeeded!</h3>
                    <v-spacer class="my-5"></v-spacer>
                    <v-btn to='/login' color="primary lighten-2" text>Log me back in.</v-btn>
                    <v-spacer class="my-5"></v-spacer>
                </v-row>
            </v-layout>
        </v-container>
    </v-main>
</template>

<script>

import { createNamespacedHelpers } from 'vuex'

const { mapGetters } = createNamespacedHelpers('app')

export default {
  name: 'AccountConfirmation',
  computed: {
    ...mapGetters({
      loading: 'loading'
    }),
    token () {
      return this.$route.query.token
    }
  },
  mounted: function () {
    this.$store.dispatch('user/CONFIRMNEWACCOUNT', this.token, { root: true })
  },
  data: () => {
    return {
    //   loading: true
    }
  }
}
</script>

<style scoped>
.background_image {
    z-index: 1;
}

.foreground_text {
    z-index: 1000;
}
</style>
