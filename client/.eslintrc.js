module.exports = {
  env: {
    browser: true,
    es6: true,
    jest: true
  },
  extends: 'standard',
  globals: {
    Atomics: 'readonly',
    SharedArrayBuffer: 'readonly'
  },
  parser: 'vue-eslint-parser',
  parserOptions: {
    parser: '@babel/eslint-parser',
    ecmaVersion: 2018,
    sourceType: 'module',
    vueFeatures: {
      filter: true,
      interpolationAsNonHTML: true,
      styleCSSVariableInjection: true
    }
  },
  plugins: ['vue'],
  rules: {}
}
