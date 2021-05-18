import Vue from 'vue'

const idExistsInList = (iterable, id) => {
  if (iterable.length === 0) return false
  return iterable.find(x => x.id === id) || false
}

const existsInList = (iterable, item) => {
  if (iterable.length === 0) return false
  return iterable.find(x => x === item) || false
}

function unique(array, propertyName) {
  return array.filter((e, i) => array.findIndex(a => a[propertyName] === e[propertyName]) === i);
}

export default {
  TOGGLE_APP_LOADING (state, payload) {
    state.loading = payload
  },
  TOGGLE_APP_LOGGED_IN (state, payload) {
    state.loggedIn = payload
  },
  TOGGLE_APP_DRAWER (state, _payload) {
    state.drawer = !state.drawer
  },
  TOGGLE_APP_DRAWER_MINIFIED (state, _payload) {
    state.drawerMinified = !state.drawerMinified
  },
  TOGGLE_APP_INVITE_MODAL (state, _payload) {
    state.inviteModalVisible = !state.inviteModalVisible
  },
  TOGGLE_APP_STATUS (state, status) {
    state.status = status
  },
  RESET_QUESTION_SEARCH (state, _payload) {
    state.questionSearch = []
  },
  UPDATE_QUESTION_SEARCH (state, payload) {
    let mergedResults = [...state.questionSearch, ...payload]
    // persit unique results
    state.questionSearch = unique([...new Set(mergedResults)], 'id')
  },
  ADD_SELECTED_QUESTIONS (state, payload) {
    if (!idExistsInList(state.questionList, payload.id)) {
      state.questionList.push(payload)
    }
  },
  TOGGLE_ERROR (state, payload) {
    state.error = payload || {}
  },
  REMOVE_SELECTED_QUESTIONS (state, payload) {
    if (state.questionList.length === 0) return
    const deleteIdx = state.questionList.findIndex(x => x.id === payload.id)
    state.questionList.splice(deleteIdx, 1)
  },
  UPDATE_KIS (state, kis) {
    const newobj = {}
    kis.forEach(ki => {
      const topic = ki[0]
      const knowledgeItem = ki[1]
      if (topic in newobj) {
        if (!existsInList(newobj[topic], knowledgeItem)) {
          newobj[topic].push(knowledgeItem)
        }
      } else {
        newobj[topic] = []
        newobj[topic].push(knowledgeItem)
      }
    })
    // state.knowledgeItems = newobj
    Vue.set(state, 'knowledgeItems', newobj)
  },
  UPDATE_TOPICS (state, topics) {
    state.topics = []
    topics.forEach(topic => {
      if (!existsInList(state.topics, topic)) {
        state.topics.push(topic)
      }
    })
  },
  UPDATE_SUBJECTS (state, subjects) {
    state.subjects = []
    state.subjects = subjects
  },
  RESET_QUIZ_CREATOR (state) {
    state.questionSearch = []
    delete state.knowledgeItems
    state.knowledgeItems = {}
    state.topics = []
    state.questionList = []
  }
}
