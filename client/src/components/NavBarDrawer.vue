<template>
  <v-navigation-drawer
    id="app-drawer"
    v-model="drawer"
    :mini-variant.sync="drawerMinified"
    color="primary"
    floating
    dark
    mobile-break-point="400"
    persistent
    fixed
    app
  >
    <template v-slot:prepend>
      <div class="d-flex my-3">
        <v-toolbar-title v-if="!drawerMinified" class="white--text mx-4 px-9">
          <a class="text-decoration-none white--text d-flex align-content-center text-center" href="/">
            <p class="font-weight-light">Zen</p>
            <p>Teach</p>
          </a>
        </v-toolbar-title>

        <v-img v-else src='../assets/icon.png' height="32" width="32" class="blue darken-1" aspect-ratio="1" contain></v-img>
        <v-spacer class="m-12" fill-height></v-spacer>
        <div>
          <v-btn fab x-small class="white blue--text mx-n4" @click="toggleMiniview()">
            <v-icon>{{ drawerMinified ? "mdi-arrow-right" : "mdi-arrow-left" }}</v-icon>
          </v-btn>
        </div>
      </div>
    </template>

    <v-divider class="mx-1 mb-1 white" inset/>

    <v-list nav>
      <v-subheader v-if="!drawerMinified">Main Menu</v-subheader>
      <v-list-item
        v-for="item in main_menu_items"
        :key="item.title"
        link
        :to="item.to"
        active-class="primary white--text"
      >
        <v-list-item-icon>
          <v-icon>{{ item.icon }}</v-icon>
        </v-list-item-icon>

        <v-list-item-content>
          <v-badge v-if="item.beta"
            color="primary darken-3"
            content="NEW"
            offset-x="2.9rem"
            offset-y="1.2rem"
            right>
            <v-list-item-title>
              {{ item.title }}
            </v-list-item-title>
          </v-badge>
          <v-list-item-title v-else>
            {{ item.title }}
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>

      <v-divider class="mx-3 mb-3" />

      <v-subheader v-if="!drawerMinified">My Content</v-subheader>
      <v-list-item
        v-for="item in my_content_items"
        :key="item.title"
        link
        :to="item.to"
        active-class="primary white--text"
      >
        <v-list-item-icon>
          <v-icon>{{ item.icon }}</v-icon>
        </v-list-item-icon>

        <v-list-item-content>
          <v-badge v-if="item.beta"
            color="primary darken-3"
            content="NEW"
            offset-x="2.9rem"
            offset-y="1.2rem"
            right>
            <v-list-item-title>
              {{ item.title }}
            </v-list-item-title>
          </v-badge>
          <v-list-item-title v-else>
            {{ item.title }}
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </v-list>
    <template v-slot:append>
      <div v-if="!drawerMinified" class="my-5 mx-4 px-3 py-5 white--text invite_box_border">
        <div class="text-center py-1">
          <v-icon class="my-1">
            mdi-help-circle-outline
          </v-icon>
        </div>
        <p class="px-2 body-1 text-center">Do you like our app? Invite your friends</p>
        <v-btn text class="primary darken-3 mx-3" @click.capture.stop="toggleInviteUserDialog">
          Send an invite
        </v-btn>
      </div>
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
      main_menu_items: [
        {
          title: 'Dashboard',
          icon: 'mdi-view-dashboard',
          to: '/'
        }
      ],
      my_content_items: [
        {
          title: 'Classrooms',
          icon: 'mdi-book-minus-multiple',
          to: '/classrooms'
        },
        {
          title: 'Question Library',
          icon: 'mdi-library-shelves',
          to: '/questions',
          beta: false
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
.invite_box_border {
  border: 2px solid #017EFA;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 10px;
}
</style>
