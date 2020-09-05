<template>
    <v-main>
        <v-container fluid fill-height>
            <v-layout>
                <v-row justify class="pa-5 flex-column justify-center align-content-center">
                    <h1 class="pa-5 text-center"> Not found!</h1>
                    <v-img src="../assets/not_found.png" width="500" class="grey lighten-4" aspect-ratio="1.5" contain></v-img>
                    <v-btn to="/" class="pa-5" text small>Back to home</v-btn>
                </v-row>
            </v-layout>
        </v-container>
    </v-main>
</template>

<script>
export default {
  name: 'NotFound'
}
</script>
