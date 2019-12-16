import Vue from "vue"
import GAuth from 'vue-google-oauth2'

const GAUTH_CLIENT_ID = process.env.VUE_APP_GAUTH_CLIENT_ID


const gauthOption = {
	clientId: GAUTH_CLIENT_ID,
	scope: "https://www.googleapis.com/auth/script.projects https://www.googleapis.com/auth/script.projects.readonly https://www.googleapis.com/auth/script.deployments https://www.googleapis.com/auth/script.deployments.readonly https://www.googleapis.com/auth/forms https://www.googleapis.com/auth/forms.currentonly",
	prompt: 'consent',
	fetch_basic_profile: false
}
Vue.use(GAuth, gauthOption)
