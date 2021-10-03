<template>
  <v-app-bar app flat max-height="88" height="60" min-height="40" id="core-bar-app">
    <v-toolbar-title class="tertiary--text font-weight-light align-self-center">
      <v-btn v-if="responsive" @click="toggleNavDrawer" icon>
        <v-icon>mdi-chevron-double-right</v-icon>
      </v-btn>
      {{ title }}
    </v-toolbar-title>

    <v-spacer />

    <v-toolbar-items>
      <v-row align="center" class="mx-0">
        <v-btn to="/user-profile" icon>
          <v-icon color="tertiary">mdi-account</v-icon>
        </v-btn>
        <v-btn @click="logout" depressed text icon>
          <v-icon right>exit_to_app</v-icon>
        </v-btn>
      </v-row>
    </v-toolbar-items>
  </v-app-bar>
</template>

<script>
import { createNamespacedHelpers } from 'vuex'

const { mapMutations: appMutations } = createNamespacedHelpers('app')
const { mapMutations: userMutations } = createNamespacedHelpers('user')

export default {
  name: 'NavBar',
  methods: {
    ...appMutations({
      toggleNavDrawer: 'TOGGLE_APP_DRAWER'
    }),
    ...userMutations({
      signoutUser: 'SIGNOUT_USER'
    }),
    logout () {
      this.signoutUser()
      this.$router.push('/login')
    },
    onResponsiveInverted () {
      if (window.innerWidth < 991) {
        this.responsive = true
      } else {
        this.responsive = false
      }
    }
  },
  mounted () {
    this.onResponsiveInverted()
    window.addEventListener('resize', this.onResponsiveInverted)
  },
  beforeDestroy () {
    window.removeEventListener('resize', this.onResponsiveInverted)
  },
  watch: {
    $route (val) {
      this.title = val.name
    }
  },
  data () {
    return {
      profile: {},
      responsive: false,
      title: null
    }
  }
}
</script>

<style scoped>
#core-app-bar {
  width: auto;
}

#core-app-bar a {
  text-decoration: none;
}
</style>
