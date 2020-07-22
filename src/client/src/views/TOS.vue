<template>
    <v-layout justify-center>
        <terms-of-service-agreement />
    </v-layout>
</template>

<script>
import TermsOfServiceAgreement from '@/components/TermsOfServiceAgreement'

export default {
  name: 'TermsOfService',
  components: {
    TermsOfServiceAgreement
  }
}
</script>
