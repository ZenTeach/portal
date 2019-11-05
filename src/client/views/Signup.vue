<template>
  <v-content>
    <v-container fluid fill-height>
      <v-layout align-center justify-center>
        <v-flex xs12 sm10 md6>
					<ValidationObserver ref="observer" v-slot="{ invalid, validated }">
          <v-card class="elevation-3">
            <v-toolbar color="grey lighten-3" flat>
              <v-toolbar-title>Signup</v-toolbar-title>
              <v-spacer></v-spacer>
            </v-toolbar>
            <v-card-text>
              <v-form>
								<ValidationProvider rules="required" name="firstname" v-slot="{ errors, valid }">
                <v-text-field
                  v-model="firstname"
                  label="Firstname"
									:error-messages="errors"
                  placeholder
                  prepend-icon="person"
                  outline
									required
                ></v-text-field>
								</ValidationProvider>

								<ValidationProvider rules="required" name="lastname" v-slot="{errors, valid}">
                <v-text-field
                  v-model="lastname"
                  label="Lastname"
                  placeholder
									:error-messages="errors"
                  prepend-icon="person"
                  outline
                  required
                ></v-text-field>
								</ValidationProvider>

								<ValidationProvider rules="required|email" name="email" v-slot="{errors, valid}">
								<v-text-field
                  v-model="email"
									:error-messages="errors"
                  label="Email"
                  placeholder
                  prepend-icon="email"
                  outline
                  required
                ></v-text-field>
								</ValidationProvider>

								<ValidationProvider rules="required" name="dob" v-slot="{errors, valid}">
                <v-text-field
                  v-model="dob"
                  label="Date of Birth"
                  placeholder
									:error-messages="errors"
                  type="date"
                  prepend-icon="calendar"
                  outline
                  required
                ></v-text-field>
								</ValidationProvider>

								<ValidationProvider rules="required|min:12" name="password" v-slot="{errors, valid}" vid="password">
                <v-text-field
                  id="password"
                  v-model="password"
									ref="password"
									:error-messages="errors"
                  label="Password"
                  name="password"
                  prepend-icon="lock"
                  outline
                  required
                  type="password"
                ></v-text-field>
								</ValidationProvider>

								<ValidationProvider rules="required|confirmed:password" name="passwordConfirmation" v-slot="{errors, valid}">
                <v-text-field
                  id="password-confirmation"
                  v-model="passwordConfirmation"
									:error-messages="errors"
                  label="Confirm Password"
                  name="password_confirmation"
                  prepend-icon="lock"
                  outline
                  required
                  type="password"
                ></v-text-field>
								</ValidationProvider>
              </v-form>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn :disabled="invalid || !validated" color="primary lighten-2" outlined class="mr-4" @click="processSignup">Signup</v-btn>
            </v-card-actions>
            <v-spacer></v-spacer>
          </v-card>
					</ValidationObserver>
        </v-flex>
      </v-layout>
    </v-container>
  </v-content>
</template>

<script>
import {
  ValidationObserver,
  ValidationProvider
} from "vee-validate";

export default {
	name: "Signup",
	components: {
    ValidationProvider,
    ValidationObserver
  },
  data() {
    return {
      valid: true,
      email: "",
      firstname: "",
      lastname: "",
      dob: null,
      password: "",
      passwordConfirmation: "",
      checkbox: false,
      lazy: false
    };
  },
  methods: {
		checkValidity() {
			return this.$refs.observer.validate();
		},
    processSignup() {
			if(this.checkValidity) {
				this.$store.dispatch("user/REGISTER_USER",{
					firstname: this.firstname,
					lastname: this.lastname,
					email: this.email,
					password: this.password,
					date_of_birth: this.dob,
					role: "Teacher"
				}, {root: true});

				this.$router.push("/");
			}
		}
  }
};
</script>
