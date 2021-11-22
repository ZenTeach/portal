<template>
  <v-app id="inspire">
    <keep-alive>
      <nav-bar v-if="isLoggedIn && !isQuizView" />
    </keep-alive>
    <nav-bar-drawer v-if="isLoggedIn && !isQuizView" />
    <v-content class="grey lighten-3">
      <unconfirmed-account-banner v-if="isLoggedIn && !isUserConfirmed" />
      <div id="core-view">
        <v-container fluid>
          <v-fade-transition mode="in-out">
            <material-notification
              v-if="this.hasError"
              :color="this.notificationColorFromStatus()"
              class="mb-3"
              icon="mdi-bell-plus"
              max-width="350px"
              mode="fade"
            >
              {{ errorMessage }}
            </material-notification>
          </v-fade-transition>
          <v-fade-transition mode="out-in">
            <keep-alive max="10">
              <router-view>
              </router-view>
            </keep-alive>
          </v-fade-transition>
          <v-dialog
              v-model="isInviteVisible"
              scrollable
              persistent
              :overlay="false"
              max-width="500px"
              transition="dialog-transition"
          >
            <invite-user/>
          </v-dialog>
        </v-container>
      </div>
      <footer>
        <v-col
          class="text-center flex items-center"
          cols="12"
        >
          <p class="font-weight-medium caption"> Copyright &#169; 2019 - {{ new Date().getFullYear() }} — ZenTeach&#174;</p>
          <a href="/tos" class="caption text-decoration-none black--text">
            Terms of Service
          </a> |
          <a href="/privacy_policy" class="caption text-decoration-none black--text">
            Privacy Policy
          </a>
        </v-col>
      </footer>
    </v-content>
  </v-app>
</template>

<script>
import NavBar from '@/components/NavBar'
import NavBarDrawer from '@/components/NavBarDrawer'
import MaterialNotification from '@/components/Notification'
import InviteUser from '@/components/InviteUser'
import UnconfirmedAccountBanner from '@/components/UnconfirmedAccountBanner'
import { createNamespacedHelpers } from 'vuex'

const { mapState, mapGetters, mapMutations } = createNamespacedHelpers('app')
const { mapGetters: mapUserGetters } = createNamespacedHelpers('user')

export default {
  components: {
    NavBar,
    NavBarDrawer,
    MaterialNotification,
    UnconfirmedAccountBanner,
    InviteUser
  },
  computed: {
    ...mapState({
      isLoggedIn: state => state.loggedIn,
      error: state => state.error,
      isInviteVisible: state => state.inviteModalVisible,
      hasError: state => {
        return Object.keys(state.error).length > 0 &&
          state.error.constructor === Object
      }
    }),
    ...mapGetters({
      appStatus: 'statusText'
    }),
    ...mapUserGetters({
      currentUser: 'getCurrentUser'
    }),
    errorMessage () {
      return this.error.message || ''
    },
    isQuizView: function () {
      const quizViewRegEx = new RegExp('(/)(quiz_view)')
      return quizViewRegEx.test(this.$route.path) || false
    },
    isUserConfirmed: function () {
      return this._.get(this.currentUser, 'confirmed', false)
    },
    isMobile: function () {
      return ['md', 'sm', 'xs'].includes(this.$vuetify.breakpoint.name)
    }
  },
  mounted () {
    console.log('Calling mounted function')
    this.$store.dispatch('settings/fetchExamBoards', {}, { root: true })
  },
  methods: {
    ...mapMutations({
      toggleNavDrawer: 'TOGGLE_APP_DRAWER'
    }),
    notificationColorFromStatus () {
      switch (this.appStatus) {
        case 'error':
          return 'error'
        case 'success':
          return 'success'
        default:
          return 'info'
      }
    },
    closeErrorBar () {
      this.$store.dispatch('app/TOGGLE_ERROR', {}, { root: true })
    }
  }
}
</script>
