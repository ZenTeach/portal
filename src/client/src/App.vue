<template>
  <v-app id="inspire">
    <nav-bar v-if="isLoggedIn && !isQuizView" />
    <nav-bar-drawer v-if="isLoggedIn && !isQuizView" />
    <v-content class="grey lighten-3">
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
              dismissible
            >
              {{ errorMessage }}
            </material-notification>
          </v-fade-transition>
          <v-fade-transition mode="out-in">
            <router-view />
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
    </v-content>
  </v-app>
</template>

<script>
import NavBar from '@/components/NavBar'
import NavBarDrawer from '@/components/NavBarDrawer'
import MaterialNotification from '@/components/Notification'
import InviteUser from '@/components/InviteUser'
import { createNamespacedHelpers } from 'vuex'
const { mapState, mapGetters } = createNamespacedHelpers('app')

export default {
  components: {
    NavBar,
    NavBarDrawer,
    MaterialNotification,
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
    errorMessage () {
      return this.error.message || ''
    },
    isQuizView: function () {
      const quizViewRegEx = new RegExp('(/)(quiz_view)')
      return quizViewRegEx.test(this.$route.path) || false
    }
  },
  mounted: function () {
    if (this.isLoggedIn) {
      this.$store.dispatch('user/FETCHCURRENTUSER', {}, { root: true })
    }
  },
  data () {
    return {
      drawer: false,
      errorColor: 'error'
    }
  },
  methods: {
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
