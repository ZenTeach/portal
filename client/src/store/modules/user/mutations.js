const TOGGLECURRENTUSER = (state, payload) => {
  state.current_user = payload
}

const SET_USER_LOADING = (state, payload) => {
  state.loading = payload
}

export default {
  TOGGLECURRENTUSER,
  SET_USER_LOADING
}
