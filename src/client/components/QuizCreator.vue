<template>
	<v-stepper v-model="curator">
                <v-stepper-header>
                  <v-stepper-step step="1" editable :complete="curator > 1">Topic selection</v-stepper-step>

                  <v-divider></v-divider>

                  <v-stepper-step step="2" editable :complete="curator > 2">Choose questions</v-stepper-step>

                  <v-divider></v-divider>

                  <v-stepper-step step="3" editable :complete="curator > 3">Select variants & finalize quiz</v-stepper-step>
                </v-stepper-header>

                <v-stepper-items>
                  <v-stepper-content step="1">
                    <v-card color="grey lighten-4" class="mx-auto">
                      <v-card-title>Select topics and knowledge items</v-card-title>
                      <v-card-text>
						<v-text-field
							name="max_score"
							label="Maximum Score"
							outline
							v-model="quizMaxScore"
						></v-text-field>
						<v-select
							:items="questionTopics"
							required
							label="Topic: "
							v-model="topicSelected"
							:rules="[() => topicSelected.length > 0 || 'You must choose at least one']"
						></v-select>

						<v-spacer class="ma-3 mb-3"></v-spacer>

						<v-select
							label="Knowledge Items: "
							multiple
							chips
							required
							:items="filteredKnowledgeItems"
							:rules="[() => selectedKnowledgeItems.length > 0 || 'You must choose at least one']"
							v-model="selectedKnowledgeItems"
						></v-select>
					</v-card-text>
                      <v-card-actions>
                        <v-btn color="primary" @click="curator = 2">Continue</v-btn>
                        <v-btn @click.native.prevent="closeDialog()">Cancel</v-btn>
                      </v-card-actions>
                    </v-card>
                  </v-stepper-content>
                  <v-stepper-content step="2">
                    <v-card color="grey lighten-4" class="mx-auto">
					<v-card-title>Search for Questions</v-card-title>
					<v-card-text>
						<question-search v-bind:subject="subject" v-bind:topic="topicSelected" v-bind:knowledge_items="selectedKnowledgeItems" v-on:update:searchResult="populateSearchResult"/>
						<question-search-result v-bind:resultSet="questionSearch" v-show="hasSearchResult"/>
					</v-card-text>
                      <v-card-actions>
                        <v-btn color="primary" @click="curator = 3">Continue</v-btn>
                        <v-btn @click.native.prevent="closeDialog()">Cancel</v-btn>
                      </v-card-actions>
                    </v-card>
                  </v-stepper-content>
                  <v-stepper-content step="3">
                    <v-card color="grey lighten-4" class="mx-auto">
                      <v-card-title>Select quiz variants</v-card-title>
                      <v-card-text>
						<v-select
							:items="Array.of(1,2,3,4)"
							v-model="variantsSelected"
							label="Variants"
						></v-select>
						</v-card-text>
                      <v-card-actions>
                        <v-btn color="primary" @click="createQuiz()">Continue</v-btn>
                        <v-btn @click.native.prevent="closeDialog()">Cancel</v-btn>
                      </v-card-actions>
                    </v-card>
                  </v-stepper-content>
                </v-stepper-items>
              </v-stepper>
</template>

<script>
import QuestionSearch from '../components/QuestionSearch';
import QuestionSearchResult from '../components/QuestionSearchResult';

import { createNamespacedHelpers } from 'vuex';
const { mapState } = createNamespacedHelpers('app');

export default {
	name: "QuizCreator",
	components: {
		QuestionSearch,
		QuestionSearchResult
	},
	computed: {
		...mapState(['questionSearch', 'questionList']),
		subject () {
			let classData = this.$store.getters["classrooms/CLASSLIST"];
			let filtered = classData.find( x => {
				let class_id = parseInt(this.$route.params.id)
				return x.id === class_id
			});
			return filtered.subject;
		},
		filteredKnowledgeItems() {
			const filterKey = this.topicSelected;
			return this.questionKnowledgeItems[filterKey] || {};
		}
	},
	data() {
		return this.initial();
	},
	methods: {
		initial() {
			return {
				curator: 1,
				quizMaxScore: 0,
				questionSearchResult: [],
				hasSearchResult: false,
				questionTopics: ["Atomic Structure", "Chemical Bonds"],
				topicSelected: "",
				questionKnowledgeItems: {
					"Atomic Structure": ["DEFINITION ATOM", "ELECTRON MASS AND CHARGE", "DEFINITION ELEMENT"],
					"Chemical Bonds": ["DEFINITION MIXTURE", "DEFINITION COMPOUND"]
				},
				selectedKnowledgeItems: [],
				variantsSelected: 1
			}
		},
		async createQuiz() {
			let payload = {
				subject: 'Chemistry',
				max_score: this.quizMaxScore,
				class_id: this.$route.params.id,
				variants: this.variantsSelected,
				questions: this.questionList
			}
			const _api = window._vm.$http;
			await _api.post(
				"http://localhost:5001/api/v1/class_quiz",
				payload
			);

			this.closeDialog();
		},
		closeDialog() {
			this.$emit("update:quizCreatorDialog", false);
			Object.assign(this.$data, this.initial());
		},
		populateSearchResult(e) {
			this.hasSearchResult = e;
		},
	}
}
</script>
