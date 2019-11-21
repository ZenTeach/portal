import actions from "./actions";
import getters from "./getters";
import mutations from "./mutations";

const state = {
  class_list: [],
  current_class: {}
};

export default {
  namespaced: true,
  state,
  actions,
  getters,
  mutations
};
