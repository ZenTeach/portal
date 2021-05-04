import { required, email, max, min, confirmed, required_if, min_value, max_value } from 'vee-validate/dist/rules'
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

extend('required_if', {
  ...required_if,
  message: (fieldName, placeholders) => {
    return `This field is needed when setting ${placeholders.target} with value ${placeholders.values}`
  }
})

extend('min_value', {
  ...min_value,
  message: 'The minimum value for this field is not met.'
})

extend('max_value', {
  ...max_value,
  message: 'The maximum value for this field is not met.'
})
