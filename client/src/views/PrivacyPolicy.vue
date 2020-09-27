<template>
    <v-layout justify-center>
        <privacy-policy />
    </v-layout>
</template>

<script>
import PrivacyPolicy from '@/components/PrivacyPolicy'

export default {
  name: 'PrivacyPolicyView',
  components: {
    PrivacyPolicy
  }
}
</script>
