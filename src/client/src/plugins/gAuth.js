import Vue from "vue"
import GAuth from 'vue-google-oauth2'

const GAUTH_CLIENT_ID = process.env.VUE_APP_GAUTH_CLIENT_ID


const gauthOption = {
	clientId: GAUTH_CLIENT_ID,
	scope: 'profile email',
	prompt: 'select_account'
}
Vue.use(GAuth, gauthOption)
