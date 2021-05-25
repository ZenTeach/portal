const QuestionCRUDMixin = {
  // watchers
  name: 'QuestionCRUDable',
  watch: {
    'questionObject.subject': function (val) {
      this.suggestedExamBoardsForSubjects(val)
    },
    getKis: function (val) {
      this.knowledge_items = []
      this.knowledge_items = this._.flatten(this._.values(this.getKis))
    }
  },
  // mounted methods
  mounted: function () {
    const enabledSubjects = this._.filter(this.getSubjects, ['enabled', true])
    this.subjects = this._.map(enabledSubjects, 'name')

    this.exam_boards = this._.reverse(this._.sortBy(this.exam_boards, ['suggested']))
  },
  // methods
  methods: {
    initData () {
      return {
        subjects: [],
        default_exam_board: [
          { value: 'aqa', text: 'AQA', suggested: false },
          { value: 'ocr_gateway', text: 'OCR Gateway', suggested: false },
          { value: 'edexcel', text: 'EdExcel', suggested: false },
          { value: 'ocr_new', text: 'OCR 21st Century', suggested: false },
          { value: 'wjec', text: 'WJEC', suggested: false },
          { value: 'ccea', text: 'CCEA', suggested: false },
          { value: 'eduqas', text: 'Eduqas', suggested: false }
        ],
        exam_boards: [],
        question_type: [
          { text: 'Multiple Choice', value: 'multiple_choice' },
          { text: 'Short Answer', value: 'short_answer' },
          { text: 'Long Answer', value: 'long_answer' }
        ],
        knowledge_items: []
      }
    },
    triggerTopicFetch () {
      this.fetchTopics(this.questionObject.subject)
    },
    triggerKIFetch () {
      const payload = {
        topics_selected: [this.questionObject.topic]
      }
      this.fetchKis(payload)
    },
    suggestedExamBoardsForSubjects (selectedSubject) {
      const subjectWithExamBoards = this._.zip(
        this._.map(this.classList, 'subject.name'),
        this._.map(this.classList, 'exam_board'))
      this.exam_boards = Array.from(this.default_exam_board)

      subjectWithExamBoards.forEach((subjectWithExamBoard) => {
        const index = this._.findIndex(this.exam_boards, ['value', subjectWithExamBoard[1]])

        if (selectedSubject === subjectWithExamBoard[0]) {
          this.exam_boards[index].suggested = true
        }
      })

      this.exam_boards = this._.reverse(this._.sortBy(this.exam_boards, ['suggested']))
    },
    validate () {
      if (this.$refs._observer.validate()) {
        return true
      }
      return false
    }
  },
  components: {}
}

export {
  QuestionCRUDMixin
}
