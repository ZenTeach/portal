import mutations from '@/store/modules/user'
import Vuex from 'vuex'

const { TOGGLECURRENTUSER } = mutations

describe("Mutation testing", () => {
	let store
	beforeEach(() => {
		store = new Vuex({
			state: {
				current_user: {}
			}
		})
	})

	it ("toggles the current user", () => {
		const payload = {
			"user": {
				"classes": [
				  {
					"id": 1,
					"name": "Atoms",
					"quizzes": [],
					"start_date": "2020-01-14T00:00:00",
					"students": [
					  {
						"classes": [
						  "/api/v1/school_class/1"
						],
						"date_of_birth": "2002-01-01T00:00:00",
						"email": "peter.griffin@example.com",
						"firstname": "peter",
						"id": 1,
						"lastname": "griffin",
						"role": "Student"
					  }
					],
					"subject": "Chemistry"
				  }
				],
				"date_of_birth": "1970-01-01T00:00:00",
				"email": "connect@ngetahun.me",
				"firstname": "john",
				"id": 1,
				"lastname": "doe",
				"role": "Teacher"
			  }
		}

		TOGGLECURRENTUSER(store, payload)
		expect(store.state.current_user).toBe(payload)
	})
})
