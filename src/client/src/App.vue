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
				</v-container>
      </div>
    </v-content>
  </v-app>
</template>

<script>
import NavBar from "@/components/NavBar";
import NavBarDrawer from "@/components/NavBarDrawer";

import { createNamespacedHelpers } from "vuex";
const { mapGetters, mapState } = createNamespacedHelpers("app");

export default {
  components: {
    NavBar,
    NavBarDrawer
  },
  computed: {
    ...mapState({
			isLoggedIn: state => state.loggedIn
    })
	},
	updated: function() {
		if (this.isLoggedIn) {
			this.$store.dispatch("user/FETCHCURRENTUSER", {}, {root: true});
		}
	},
  data() {
    return {
      drawer: false
    };
  },
};
</script>
