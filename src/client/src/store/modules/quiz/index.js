import actions from "./actions";
import getters from "./getters";
import mutations from "./mutations";

const state = {
	quiz_questions: []
}

export default {
	namespaced: true,
	state,
	actions,
	getters,
	mutations
  };
