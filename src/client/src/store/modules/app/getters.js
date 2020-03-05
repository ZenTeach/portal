export default {
  loggedIn(state) {
    return state.loggedIn;
  },
  loading(state) {
    return state.loading;
  },
  getDrawer(state) {
    return state.drawer;
  },
  getDrawerMinified(state) {
    return state.drawerMinified;
  },
  getQuestionResult(state) {
    return state.questionSearch;
  },
  getQuestionList(state) {
    return state.questionList;
  },
  getError(state) {
    return state.error;
  }
};
