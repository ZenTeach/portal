import {
  loginUser,
  logoutUser,
  registerUser,
  getCurrentUser
} from "../../../service/user_auth";

const LOGIN_USER = ({ commit }, payload) => {
  commit("app/TOGGLE_APP_LOADING", true, { root: true });
  const { status } = loginUser(payload);
  commit("app/TOGGLE_APP_LOGGED_IN", true, { root: true });
  commit("app/TOGGLE_APP_LOADING", false, { root: true });
};

const SIGNOUT_USER = ({ commit }) => {
  commit("app/TOGGLE_APP_LOADING", true, { root: true });
  logoutUser();
  commit("app/TOGGLE_APP_LOGGED_IN", false, { root: true });
  commit("TOGGLECURRENTUSER", {});
  commit("app/TOGGLE_APP_LOADING", false, { root: true });
};

const REGISTER_USER = ({ commit }, payload) => {
  commit("app/TOGGLE_APP_LOADING", true, { root: true });
  const result = registerUser(payload);
  commit("app/TOGGLE_APP_LOGGED_IN", true, { root: true });
  commit("app/TOGGLE_APP_LOADING", false, { root: true });
};

const FETCHCURRENTUSER = ({ commit }) => {
  commit("app/TOGGLE_APP_LOADING", true, { root: true });

  getCurrentUser().then(result => {
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
