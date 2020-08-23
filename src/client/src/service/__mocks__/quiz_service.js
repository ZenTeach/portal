export default {
  submitQuiz: jest.fn(() => Promise.resolve({ data: {} })),
  startQuiz: jest.fn(() => Promise.resolve({ data: {} })),
  fetchQuiz: jest.fn(() => Promise.resolve({ data: {} })),
  fetchReportCard: jest.fn(() => Promise.resolve({ data: {} })),
  fetchGradedReportCards: jest.fn((_someId) => Promise.resolve({
    data: [{
      grade_breakdown: [
        {
          feedback: [
            'Look at these images.',
            'Look at these images.',
            'Revise theses lesson slides.'
          ],
          knowledge_item: [
            'MASS',
            'MASS',
            'NEUTRON MASS AND CHARGE'
          ],
          progress: [
            '0/1',
            '0/1',
            '0/1'
          ],
          topic: 'Atomic Structure'
        },
        {
          feedback: [
            'Look at these images.'
          ],
          knowledge_item: [
            'DEFINITION MIXTURE'
          ],
          progress: [
            '0/1'
          ],
          topic: 'Chemical Bonds'
        }
      ],
      score: 3,
      student: {
        classes: [
          '/api/v1/school_class/42'
        ],
        email: 'peter.griffin@example.com',
        firstname: 'peter',
        id: 42,
        lastname: 'griffin'
      },
      uuid: 'a8196676-efd3-475e-8308-90eca5a90618'
    }]
  }))
}
