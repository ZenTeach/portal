<template>
	<v-container fluid>
			<v-row class="ma-4 pa-3" :justify="center" :align="start">
				<!-- Title -->
				<v-col class="ma-2">
					<h1>{{ quiz["name"]}} </h1>
				</v-col>
			</v-row>
			<v-row class="mx-10 pa-3" :align="center" :justify="space-between">
				<!-- Questions -->
				<v-col :align="center">
				<template v-for="(question, idx) in quiz['questions']" >
					<v-card :key="idx" class="ma-2" ref="">
						<v-card-text>
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
const { mapActions } = createNamespacedHelpers("quiz");

export default {
	name: "QuizView",
	components: {
		ValidationObserver,
		ValidationProvider
	},
	data() {
		return {
			quiz: {
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
	},
	computed: {

	},
	methods: {
		// ...mapActions(["SUBMBIT_QUIZ"]),
		selectChoices(val) {
			console.log(val)
		},
		submit() {

		}
	}
}
</script>
