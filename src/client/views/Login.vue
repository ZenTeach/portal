<template>
  <v-content>
    <v-container fluid fill-height>
      <v-layout align-center justify-center>
        <v-flex xs12 sm10 md6>
          <v-card class="elevation-3">
            <v-toolbar color="grey lighten-3" flat>
              <v-toolbar-title class="d-flex text-center">
                <span class="font-weight-light">Zen</span>
                <span class>Teach</span>
                <span class="mx-1">Login</span>
              </v-toolbar-title>
              <v-spacer></v-spacer>
            </v-toolbar>
            <v-card-text>
              <v-form>
                <v-text-field
                  v-model="email"
                  :rules="emailRules"
                  label="Email"
                  placeholder
                  prepend-icon="email"
                  outline
                  required
                ></v-text-field>
                <v-text-field
                  id="password"
                  v-model="password"
                  label="Password"
                  name="password"
                  prepend-icon="lock"
                  outline
                  required
                  type="password"
                ></v-text-field>
              </v-form>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn :disabled="!valid" text dark class="mr-4 primary" @click="login_user" outlined>Login</v-btn>
            </v-card-actions>
            <v-spacer></v-spacer>
            <v-divider class="mx-3 mb-3" />
            <div class="d-flex mx-3 pa-5 justify-center">
              <p class="subheading">
                <a href="/signup" class="subheading">Don't have an account yet? Sign up now</a>
              </p>
            </div>
            <v-spacer></v-spacer>
          </v-card>
        </v-flex>
      </v-layout>
    </v-container>
  </v-content>
</template>

<script>
export default {
  name: "Login",
  data: () => ({
    valid: true,
    email: "",
    emailRules: [
      v => !!v || "E-mail is required",
      v => /.+@.+\..+/.test(v) || "E-mail must be valid"
    ],
    password: "",
    checkbox: false,
    lazy: false
  }),
  computed: {},
  methods: {
    validate() {
      if (this.$refs.form.validate()) {
        return true;
      }
      return false;
    },
    login_user() {
      if (this.validate) {
        this.$store.dispatch(
          "user/LOGIN_USER",
          {
            email: this.email,
            password: this.password
          },
          { root: true }
        );
      	this.$router.push("/");
      }
    }
  }
};
</script>
