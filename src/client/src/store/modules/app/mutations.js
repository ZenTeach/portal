const existsInList = (iterable, id) => {
  if (iterable.length == 0) return false;
  return iterable.find(x => x.id == id) || false;
};

export default {
  TOGGLE_APP_LOADING(state, payload) {
    state.loading = payload;
  },
  TOGGLE_APP_LOGGED_IN(state, payload) {
    state.loggedIn = payload;
  },
  TOGGLE_APP_DRAWER(state, _payload) {
    state.drawer = !state.drawer;
  },
  TOGGLE_APP_DRAWER_MINIFIED(state, _payload) {
    state.drawerMinified = !state.drawerMinified;
  },
  RESET_QUESTION_SEARCH(state, _payload) {
    state.questionSearch = [];
  },
  UPDATE_QUESTION_SEARCH(state, payload) {
    state.questionSearch = [...state.questionSearch, ...payload];
  },
  ADD_SELECTED_QUESTIONS(state, payload) {
    // state.questionList = [...state.questionList, ...payload];
    if (!existsInList(state.questionList, payload.id)) {
      state.questionList.push(payload);
    }
  },
  REMOVE_SELECTED_QUESTIONS(state, payload) {
    if (state.questionList.length == 0) return;
    const deleteIdx = state.questionList.findIndex(x => x.id == payload.id);
    state.questionList.splice(deleteIdx, 1);
  }
};
