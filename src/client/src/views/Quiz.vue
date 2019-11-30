<template>
	<v-container id="quiz_details_view">
		<v-layout row column wrap justify-center>
			<v-row>
				<v-col cols="12" lg="5">
				</v-col>

				<v-col cols="12" lg="5">
					<!-- <v-btn
						color="success"
						:loading="gFormExportLoading"
						@click.native="handleGFormExport"
						class="white--text">
							Export to Google Forms
						<v-icon left dark>mdi-export</v-icon>
					</v-btn> -->
					<v-overflow-btn
						color="success"
          				class="my-2"
						prepend-icon="mdi-export"
          				:items="exportableLinks"
        				label="Export to:"
						target="quiz_details_view">
					</v-overflow-btn>
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
					text:'Google Form',
					callback: () => handleGFormExport()
				},
				{
					text: 'PDF',
					callback: () => handlePDFGeneration()
				}
			]
		}

	},
	methods: {
		handleGFormExport() {
			// this.$gAuth.getAuthCode()
			// 	.then(authCode => {
			// 		console.log(authCode)
			// 		return Api.post('/teacher/auth/google', {authCode: authCode})
			// 		// 4/tgHXbgZivoyy_a6ezHCYkqZB-6y5Y2D1lxhYdY_ypp95MSAH9TLdUn6i1cIkbW3Zv8JVDwKEzJgJRzEVaRC2YLA
  			// 		// on success
  			// 		// return this.$http.post('http://your-backend-server.com/auth/google', { code: authCode, redirect_uri: 'postmessage' })
			// })
		},
		handlePDFGeneration() {
			console.log("Generating PDF!")
		}
	}
}
</script>
