<template>
  <v-app
    id="inspire"
    dark
  >
    <nav-bar/>
    <div class="container mt-5">
    <router-view/>
    </div>
    <v-navigation-drawer
      v-model="drawer"
      fixed
      clipped
      app
    >
    </v-navigation-drawer>
    <v-toolbar
      color="red"
      dense
      fixed
      clipped-left
      app>
      <v-toolbar-side-icon @click.stop="drawer = !drawer"></v-toolbar-side-icon>
      <v-toolbar-title class="mr-5 align-center">
        <span class="title">ZenTeach</span>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-layout row align-center style="max-width: 650px"></v-layout>
    </v-toolbar>
    <v-content>
      <v-container fill-height>
        <v-layout justify-center align-center>
          <v-flex shrink>
            <v-tooltip right>
              <template v-slot:activator="{ on }">
              </template>
              <span>Source</span>
            </v-tooltip>
            <v-tooltip right>
              <template v-slot:activator="{ on }">
                <v-btn icon large href="https://codepen.io/johnjleider/pen/YeRKwQ" target="_blank" v-on="on">
                  <v-icon large>mdi-codepen</v-icon>
                </v-btn>
              </template>
              <span>Codepen</span>
            </v-tooltip>
          </v-flex>
        </v-layout>
      </v-container>
    </v-content>
  </v-app>
</template>

<script>
import 'jquery'
import NavBar from './components/NavBar'

export default {
  components: {
    NavBar
  },
  async created () {
    try {
      await this.$auth.renewTokens()
    } catch {
      // Supress the 'not logged in' error as we can illegitimately get that
      // when processing the callback url
    }
  },
  data: () => ({
    drawer: null
  }),
  props: {
    source: String
  }
}
</script>
