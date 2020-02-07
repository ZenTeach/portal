import {shallowMount, createLocalVue} from '@vue/test-utils'
// import Quiz from '@/views/Quiz.vue'
import VueRouter from 'vue-router'
import Vuex from 'vuex'
import { jestPreset } from 'ts-jest'
// import mockApi from 'Api'

const localVue = createLocalVue()
localVue.use(Vuex)
localVue.use(VueRouter)
const router = new VueRouter()

describe('Quiz.vue', () => {
	let actions
	let store

	beforeEach(() => {
		store = new Vuex.Store({})
	})
	it.skip('has renders the view correctly', () => {
		// jest.mock('@/services/Api', () => {
		// 	return {
		// 		post: () => {authCode: 'asjksdko'}
		// 	}
		// })
		// mockApi.post.mockImplementation(async () => {})
		const wrapper = shallowMount(Quiz, {store, localVue, router})
		expect(wrapper.isVueInstance()).toBe(true)
	})
})
