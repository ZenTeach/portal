<template>
  <v-container
    fill-height
    fluid
  >
    <v-row justify="center">
      <v-col
        cols="12"
        md="8"
      >
      </v-col>
      <v-col
        cols="12"
        md="10"
      >
        <material-card class="v-card-profile">
            <v-avatar
            slot="offset"
            class="mx-auto d-block elevation-6"
            size="130" color="indigo"
          >
            <v-icon dark>mdi-account-circle</v-icon>
          </v-avatar>
          <v-card-text class="text-center">
            <h6 class="overline mb-3">
              Teacher
            </h6>

            <h3 class="font-weight-light text-capitalize">
              {{ user.firstname }} {{ user.lastname }}
            </h3>
          </v-card-text>
        </material-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import MaterialCard from '@/components/MaterialCard'
import { createNamespacedHelpers } from 'vuex'

const { mapGetters } = createNamespacedHelpers('user')

export default {
  name: 'UserProfile',
  components: {
    MaterialCard
  },
  computed: {
    ...mapGetters({
      user: 'getCurrentUser'
    })
  }
}
</script>
