<template>
	<v-container id="quiz_details_view">
		<v-layout row column wrap justify-center>
			<v-row>
				<v-col cols="12" lg="5">
				</v-col>

				<v-col cols="12" lg="5">
					<template>
						<div class="text-center">
    						<v-menu bottom offset-y>
								<template v-slot:activator="{ on }">
								<v-btn
									color="success"
									dark
									v-on="on"
									>
									<v-icon left>mdi-share-variant</v-icon>
									Export to:
									</v-btn>
								</template>

								<v-list>
									<v-list-item
									v-for="(item, index) in exportableLinks"
									:key="index"
									@click="item.action"
									>
									<v-list-item-title>{{ item.title }}</v-list-item-title>
									</v-list-item>
								</v-list>
							</v-menu>
						</div>
					</template>
				</v-col>
			</v-row>
		</v-layout>
	</v-container>
</template>

<script>
import Api from "@/service/Api"
export default {
	name: "Quiz",
	data() {
		return {
			gFormExportLoading: false,
			exportableLinks: [
				{
					title:'Google Form',
					action: () => this.handleGFormExport()
				},
				{
					title: 'PDF',
					action: () => this.handlePDFGeneration()
				}
			]
		}

	},
	computed: {
		quiz_id (){
			return this.$route.params.id
		}
	},

	methods: {
		handleGFormExport() {
			this.$gAuth.getAuthCode()
				.then(authCode => {
					console.log(authCode)
					return Api.post('/teacher/auth/google', {authCode: authCode})
					// on success
			}).then(response => {
				Api.post(`/class_quiz/${this.quiz_id}/generate`, {
					"type": "gform"
				}).then(response => {
					console.log(response)
				})
			})

		},
		handlePDFGeneration() {
			Api.post(`/class_quiz/${this.quiz_id}/generate`, {
				"type": "pdf"
			}).then((response) => {
				// TODO: show success/error message
				console.log(response)
			})
		}
	}
}
</script>
