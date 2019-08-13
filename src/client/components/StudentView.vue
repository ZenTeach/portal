<template>
  <div>
    <v-data-table
          :headers="headers"
          :items="students"
          :expand="expand"
          item-key="name"
        >
        <template v-slot:items="props">
          <tr @click="props.expanded = !props.expanded">
            <td class="text-xs-right">{{ props.item.first_name }}</td>
            <td class="text-xs-right">{{ props.item.last_name }}</td>
            <td class="text-xs-right">{{ props.item.class_id }}</td>
          </tr>
        </template>
        <template v-slot:expand="props">
          <v-card flat>
            <v-card-text>Peek-a-boo!</v-card-text>
          </v-card>
        </template>
      </v-data-table>
      <p class="error">{{ error }}</p>
      <p class="decode-result">Last result: <b>{{ qr_result }}</b></p>
      <qrcode-stream @detect="onDetect" @decode="onDecode" @init="onInit"></qrcode-stream>
  </div>
</template>

<script>
const request = require('request')

export default {
  data: () => ({
    qr_result: 'nothing yet',
    error: 'no error yet',
    expand: false,
    headers: [
      { text: 'First name', align: 'left', value: 'first_name', width: 30 },
      { text: 'Last Name', align: 'left', value: 'last_name', width: 30 },
      { text: 'Class', align: 'left', value: 'class_id', width: 40 }
    ],
    students: []
  }),
  methods: {

    loadStudents () {
      var vueComponent = this
      request.get({ url: 'http://localhost:5000/get_students', qs: { 'class_name': 'foo' } }, (error, response, studentsJson) => {
        /* TODO: Check for some error - decide on error codes for API */
        console.log('error = ', error)
        try {
          var studentsArray = JSON.parse(studentsJson)
          vueComponent.students = studentsArray
        } catch (err) {
          console.log(err)
        }
      })
    },
    onDecode (result) {
      this.qr_result = result
    },
    async onDetect (promise) {
      try {
        const {
          imageData, // raw image data of image/frame
          content, // decoded String
          location // QR code coordinates
        } = await promise

        console.log('imageData = ', imageData)
        console.log('content = ', content)
        console.log('QR code location = ', location)
        // ...
      } catch (error) {
        console.log('error = ', error)
      }
    },
    async onInit (promise) {
      try {
        await promise
      } catch (error) {
        if (error.name === 'NotAllowedError') {
          this.error = 'ERROR: you need to grant camera access permisson'
        } else if (error.name === 'NotFoundError') {
          this.error = 'ERROR: no camera on this device'
        } else if (error.name === 'NotSupportedError') {
          this.error = 'ERROR: secure context required (HTTPS, localhost)'
        } else if (error.name === 'NotReadableError') {
          this.error = 'ERROR: is the camera already in use?'
        } else if (error.name === 'OverconstrainedError') {
          this.error = 'ERROR: installed cameras are not suitable'
        } else if (error.name === 'StreamApiNotSupportedError') {
          this.error = 'ERROR: Stream API is not supported in this browser'
        }
      }
    }
  },
  created: function () {
    // this.loadStudents()
  }
}
</script>

<style>

</style>
