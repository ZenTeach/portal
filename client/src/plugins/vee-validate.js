import { required, email, max, min, confirmed } from 'vee-validate/dist/rules'
import { extend } from 'vee-validate'

extend('required', {
  ...required,
  message: 'This field is required'
})

extend('max', {
  ...max,
  message: 'This {_field_} must be {length} characters or less'
})

extend('min', {
  ...min,
  message: 'This {_field_} must be {length} characters or greater'
})

extend('confirmed', {
  ...confirmed,
  message: 'This {_field_} should not be different.'
})

extend('email', {
  ...email,
  message: 'This field must be a valid email.'
})
