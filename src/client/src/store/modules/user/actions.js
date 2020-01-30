import {
  loginUser,
  logoutUser,
  registerUser,
  getCurrentUser
} from "../../../service/user_auth";

import Vue from "vue"

const LOGIN_USER = ({ commit }, payload) => {
  commit("app/TOGGLE_APP_LOADING", true, { root: true });
	commit("app/TOGGLE_APP_LOGGED_IN", true, { root: true });
	loginUser(payload);
  commit("app/TOGGLE_APP_LOADING", false, { root: true });
};

const SIGNOUT_USER = ({ commit }) => {
  commit("app/TOGGLE_APP_LOADING", true, { root: true });
	logoutUser();
	Vue.prototype.$cookies.remove("access_token_cookie");
  commit("app/TOGGLE_APP_LOGGED_IN", false, { root: true });
  commit("TOGGLECURRENTUSER", {});
  commit("app/TOGGLE_APP_LOADING", false, { root: true });
};

const REGISTER_USER = ({ commit }, payload) => {
  commit("app/TOGGLE_APP_LOADING", true, { root: true });
  registerUser(payload);
  commit("app/TOGGLE_APP_LOGGED_IN", true, { root: true });
  commit("app/TOGGLE_APP_LOADING", false, { root: true });
};

const FETCHCURRENTUSER = ({ commit }) => {
  commit("app/TOGGLE_APP_LOADING", true, { root: true });

  getCurrentUser().then(result => {
		console.log("Result fetched in FETCHCURRENTUSER", result)
    commit("TOGGLECURRENTUSER", result.data.user.identity);
  });
  commit("app/TOGGLE_APP_LOADING", true, { root: true });
};

export default {
  LOGIN_USER,
  SIGNOUT_USER,
  REGISTER_USER,
  FETCHCURRENTUSER
};
