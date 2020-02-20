<template>
	<v-container fluid>
			<v-row class="ma-4 pa-3" :justify="center" :align="start">
				<!-- Title -->
				<input type="hidden" />
				<v-col class="ma-2">
					<h1>{{ quizTitle }} </h1>
				</v-col>
			</v-row>
			<v-row class="mx-10 pa-3" :align="center" :justify="space-between">
				<!-- Questions -->
				<v-col :align="center">
				<template v-for="(question, idx) in quiz['questions']" >
					<v-card :key="idx" class="ma-2" ref="">
						<v-card-text ref="question_">
								<h3> {{ question.question }} </h3>
								<!-- Question choices -->
								<v-radio-group ref="question_choice" @change="selectChoices()">
									<v-radio
										v-for="(choice, idx) in question.choices"
										:key="idx"
										:label="choice"
										:value="'choice_'+idx"
										readonly
										>
									</v-radio>
								</v-radio-group>
						</v-card-text>
					</v-card>
				</template>
				</v-col>
				<v-dialog v-model="dialog" max-width="1000px" persistent>
					<p> Please enter your email to finish submitting your quiz: </p>
					<v-text-field
						placeholder="email"
						label="email"
						value=""
						single-line
						:model="studentEmail"
					></v-text-field>
					<v-btn color="success">Proceed</v-btn>
		</v-dialog>
			</v-row>

			<!-- Call to Action -->
			<v-row class="mx-10 pa-5" :align="end" :justify="end">
				<v-btn color="success" @click="submit()">
					Submit Quiz
				</v-btn>
			</v-row>
	</v-container>
</template>

<script>
import Api from "@/service/Api"

import {
  ValidationObserver,
  ValidationProvider
} from "vee-validate";
import { createNamespacedHelpers } from 'vuex';
const { mapActions, mapState } = createNamespacedHelpers("quiz");

export default {
	name: "QuizView",
	components: {
		ValidationObserver,
		ValidationProvider
	},
	data() {
		return {
			dialog: false,
			studentEmail: "",
			quiz: {
				// uid:
				name: "Chemistry Quiz",
				max_score: "3",
				questions: [
					{
					"choices": {
						"a": "The smallest piece of an element that can exist.",
						"b": "A particle that cannot be broken down any further.",
						"c": "Multiple compounds chemically bonded to each other.",
						"d": "A particle that has no mass."
					},
					"id": 10,
					"knowledge_item": "DEFINITION ATOM",
					"question": "What is an atom?",
					"question_type": 1,
					"subject": "Chemistry",
					"tag": "6",
					"topic": "Atomic Structure"
					}, {
					"choices": {
						"a": "Matter made of at least two types of atoms.",
						"b": "",
						"c": "Matter that is only made of one type of atom.",
						"d": ""
					},
					"id": 11,
					"knowledge_item": "DEFINITION ELEMENT",
					"question": "What is an element?",
					"question_type": 1,
					"subject": "Chemistry",
					"tag": "7",
					"topic": "Atomic Structure"
					}, {
					"choices": {
						"a": "Electrons have a mass of 1 and a negative charge.",
						"b": "Electrons have a mass of 0 and a negative charge.",
						"c": "Electrons have a mass of 0 and a positive charge.",
						"d": "Electrons have a mass of 0 and a neutral charge."
					},
					"id": 6,
					"knowledge_item": "ELECTRON MASS AND CHARGE",
					"question": "Which statements about electrons are correct?",
					"question_type": 1,
					"subject": "Chemistry",
					"tag": "3",
					"topic": "Atomic Structure"
				}]
			},
			selectedChoices: []
		}
	},
	mounted: function() {
		mapActions()
	},
	computed: {
		quizTitle() {
			return this.quiz.name || ""
		}
	},
	methods: {
		// ...mapActions(["SUBMBIT_QUIZ"]),
		selectChoices(val) {
			console.log(val)
		},
		submit() {

			// Step 1: Ask student to enter their email address
			this.dialog = this.dialog ^ True

			// Step 2: check if valid
			// Step 3: Create payload
			let payload = this._collect_submission()
			// Step 4: Send payload to server
		},
		_collect_submission() {
			// Submitting quiz
			// Quiz structure:
			// -> QuizID
			// StudentEmail
			// -> Data
				// For-Each Question
				// -> QuestionID
				// -> Choice Answer
			return {
				'QuizID': this.quiz.uid,
				'StudentEmail': this.studentEmail,
				'data': this.$refs['question_']
			}
		}
	}
}
</script>
