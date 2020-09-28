const CLASSLIST_UPDATED = (state, payload) => {
  state.class_list = payload
}

const CLASSLIST_ADDED = (state, payload) => {
  state.class_list.push(payload)
}

const UPDATE_CURRENT_CLASS = (state, payload) => {
  state.current_class = payload
}

export default {
  CLASSLIST_UPDATED,
  CLASSLIST_ADDED,
  UPDATE_CURRENT_CLASS
}
