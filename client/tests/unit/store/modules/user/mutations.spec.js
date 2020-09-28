import mutations from '@/store/modules/user/mutations'

const { TOGGLECURRENTUSER } = mutations

describe('User mutation', () => {
  const payload = {
    user: {
      classes: [
        {
          id: 1,
          name: 'Atoms',
          quizzes: [],
          start_date: '2020-01-14T00:00:00',
          students: [
            {
              classes: ['/api/v1/school_class/1'],
              date_of_birth: '2002-01-01T00:00:00',
              email: 'peter.griffin@example.com',
              firstname: 'peter',
              id: 1,
              lastname: 'griffin',
              role: 'Student'
            }
          ],
          subject: 'Chemistry'
        }
      ],
      date_of_birth: '1970-01-01T00:00:00',
      email: 'connect@ngetahun.me',
      firstname: 'john',
      id: 1,
      lastname: 'doe',
      role: 'Teacher'
    }
  }

  it('toggles the current user', () => {
    const state = { current_user: {} }
    TOGGLECURRENTUSER(state, payload)
    expect(state.current_user).toBe(payload)
  })
})
