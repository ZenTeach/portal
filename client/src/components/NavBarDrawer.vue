<template>
  <v-navigation-drawer
    id="app-drawer"
    v-model="drawer"
    :mini-variant.sync="drawerMinified"
    color="primary"
    floating
    dark
    mobile-break-point="991"
    persistent
    fixed
    app
  >
    <v-list-item two-line>
      <v-toolbar-title v-if="!drawerMinified" class="align-self-center text-center">
        <span class="font-weight-light">Zen</span>
        <span>Teach Portal</span>
      </v-toolbar-title>
      <v-img v-else src='../assets/icon.png' height="32" width="40" class="grey darken-1" aspect-ratio="1" contain></v-img>
    </v-list-item>

    <v-divider class="mx-3 mb-3" />

    <v-list nav>
      <v-list-item
        v-for="item in items"
        :key="item.title"
        link
        :to="item.to"
        active-class="primary white--text"
      >
        <v-list-item-icon>
          <v-icon>{{ item.icon }}</v-icon>
        </v-list-item-icon>

        <v-list-item-content>
          <v-list-item-title>
            {{ item.title }}
            <v-badge v-if="item.beta"
              color="deep-purple"
              dot
              overlap
              right>
            </v-badge>
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>

      <v-list-item active-class="primary white--text" @click.capture.stop="toggleInviteUserDialog">
        <v-list-item-icon>
          <v-icon>mdi-email</v-icon>
        </v-list-item-icon>

        <v-list-item-content>
          <v-list-item-title>Invite</v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </v-list>

    <template v-slot:append>
      <v-list nav>
        <v-list-item>
          <v-list-item-action>
            <v-btn text @click="toggleMiniview()">
              <v-icon>{{ drawerMinified ? "mdi-format-horizontal-align-right" : "mdi-format-horizontal-align-left" }}</v-icon>
            </v-btn>
          </v-list-item-action>

          <v-list-item-title class="font-weight-light" v-if="!drawerMinified">Minimize</v-list-item-title>
        </v-list-item>
      </v-list>
    </template>
  </v-navigation-drawer>
</template>

<script>
import { mapGetters, mapMutations } from 'vuex'
export default {
  name: 'NavBarDrawer',
  computed: {
    ...mapGetters({
      drawer: 'app/getDrawer',
      drawerMinified: 'app/getDrawerMinified'
    })
  },
  data: function () {
    return {
      items: [
        {
          title: 'Dashboard',
          icon: 'mdi-view-dashboard',
          to: '/'
        },
        {
          title: 'Classrooms',
          icon: 'mdi-book-minus-multiple',
          to: '/classrooms'
        },
        {
          title: 'Questions',
          icon: 'mdi-post-it-note-check',
          to: '/questions',
          beta: true
        }
      ]
    }
  },
  methods: {
    ...mapMutations(['TOGGLE_APP_DRAWER_MINIFIED']),
    toggleMiniview () {
      this.$store.commit('app/TOGGLE_APP_DRAWER_MINIFIED')
    },
    toggleInviteUserDialog () {
      this.$store.commit('app/TOGGLE_APP_INVITE_MODAL')
    }
  }
}
</script>

<style scoped>
</style>
