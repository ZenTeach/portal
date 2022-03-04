<template>
  <v-app-bar app flat max-height="88" height="60" min-height="40" id="core-bar-app">
    <v-toolbar-title class="tertiary--text font-weight-light d-flex align-center align-self-center">
      <v-btn v-if="responsive" @click="toggleNavDrawer" icon>
        <v-icon small>mdi-chevron-double-right</v-icon>
      </v-btn>
      <breadcrumb />
    </v-toolbar-title>

    <v-spacer />

    <v-toolbar-items>
      <v-row align="center" class="mx-0">
        <v-col class="d-flex align-center">
          <v-btn flat icon>
            <v-icon medium class="text--disabled">mdi-bell</v-icon>
          </v-btn>
        </v-col>
        <v-menu
          bottom
          left
        >
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              icon
              v-bind="attrs"
              v-on="on"
            >
            <v-avatar size="36px" color="blue">
              <span class="white--text text-h6">{{ initials }}</span>
            </v-avatar>
            </v-btn>
          </template>

          <v-list>
            <v-list-item
              v-for="(item, i) in user_account_items"
              :key="i"
            >
              <template v-if="item.click_action">
                <v-list-item-title @click="item.click_action" class="text-decoration-none text--primary">
                  <v-icon>{{ item.icon }}</v-icon> {{ item.title }}
                </v-list-item-title>
              </template>
              <template v-else>
                <v-list-item-title>
                  <v-icon>{{ item.icon }}</v-icon>
                  <a :class="'text-decoration-none text--primary ' + (item.to === undefined ? 'text--disabled' : '')" :href="item.to">
                    {{ item.title }}
                  </a>
                </v-list-item-title>
              </template>
            </v-list-item>
          </v-list>
        </v-menu>
      </v-row>
    </v-toolbar-items>
  </v-app-bar>
</template>

<script>
import { createNamespacedHelpers } from 'vuex'
import Breadcrumb from './Breadcrumb.vue'
const { mapMutations: appMutations } = createNamespacedHelpers('app')
const { mapActions: userActions, mapGetters: userGetters } = createNamespacedHelpers('user')

export default {
  name: 'NavBar',
  components: {
    Breadcrumb
  },
  computed: {
    ...userGetters({
      currentUser: 'getCurrentUser'
    }),
    initials () {
      const fNameInitial = this.currentUser.firstname.charAt(0)
      const lNameInitial = this.currentUser.lastname.charAt(0)
      return `${fNameInitial}${lNameInitial}`
    }
  },
  methods: {
    ...appMutations({
      toggleNavDrawer: 'TOGGLE_APP_DRAWER'
    }),
    ...userActions({
      signoutUser: 'SIGNOUT_USER'
    }),
    logout () {
      this.signoutUser().then(() => {
        this.$router.push('/login')
      })
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
      title: null,
      user_account_items: [
        {
          title: 'Profile',
          icon: 'mdi-account',
          to: '/user-profile'
        },
        {
          title: 'Account Settings',
          icon: 'mdi-settings'
          // to: '/user-settings'
        },
        {
          title: 'Logout',
          icon: 'mdi-logout',
          to: '/logout',
          click_action: this.logout
        }
      ]
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
