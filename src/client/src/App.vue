<template>
  <v-app id="inspire">
    <nav-bar v-if="isLoggedIn" />
    <nav-bar-drawer v-if="isLoggedIn" />
    <v-content class="grey lighten-3">
      <div id="core-view">
		<v-container fluid>
			<v-fade-transition mode="out-in">
				<router-view />
			</v-fade-transition>
			<!-- <material-notification
				color="error"
				class="mb-3"
				icon="mdi-bell-plus"
				max-width="350px"
				dismissible
			>
				Lorem ipsum, dolor sit amet consectetur adipisicing elit. Maiores porro id ipsum iure repellat sit tenetur quia!
			</material-notification> -->
			<v-snackbar
				v-model="this.hasError"
      			:color="errorColor"
      			right="true"
      			multi-line="true"
      			top="true"
			>
				{{ error.message }}
				<v-btn dark text @click="closeErrorBar">
					Close
				</v-btn>
			</v-snackbar>
		</v-container>
      </div>
    </v-content>
  </v-app>
</template>

<script>
import NavBar from '@/components/NavBar'
import NavBarDrawer from '@/components/NavBarDrawer'
import MaterialNotification from '@/components/Notification'
import { createNamespacedHelpers } from 'vuex'
const { mapGetters, mapState } = createNamespacedHelpers('app')

export default {
  components: {
    NavBar,
    NavBarDrawer,
    MaterialNotification
  },
  computed: {
    ...mapState({
      isLoggedIn: state => state.loggedIn,
      error: state => state.error,
      hasError: state => {
        return Object.keys(state.error).length > 0 &&
				state.error.constructor === Object
      }
    })
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
	  closeErrorBar () {
		  this.$store.dispatch('app/TOGGLE_ERROR', {}, { root: true })
	  }
  }
}
</script>
