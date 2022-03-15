module.exports = {
  moduleFileExtensions: ['js', 'jsx', 'json', 'vue'],
  transform: {
    '.*\\.(vue)$': '@vue/vue2-jest',
    '.+\\.(css|styl|less|sass|scss|svg|png|jpg|ttf|woff|woff2)$':
      'jest-transform-stub',
    '^.+\\.js$': 'babel-jest',
    'vee-validate/dist/rules': 'babel-jest'
  },
  globals: {
    '@vue/vue2-jest': {
      babelConfig: {
        plugins: ['babel-plugin-transform-object-rest-spread'],
        presets: [['env', { modules: false }]],
        env: {
          test: {
            presets: [
              [
                'env',
                {
                  modules: 'commonjs',
                  targets: {
                    node: 'current'
                  }
                }
              ]
            ]
          }
        }
      }
    }
  },
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1'
  },
  transformIgnorePatterns: [
    '/node_modules/(?!(vuetify)|(@babel)/)',
    '/node_modules/(?!vee-validate/dist/rules)'
  ],
  collectCoverage: false,
  collectCoverageFrom: ['**/*.{js,vue}', '!**/node_modules/**'],
  coverageReporters: ['html', 'text-summary'],
  snapshotSerializers: ['jest-serializer-vue'],
  testEnvironment: 'jsdom',
  testMatch: [
    '**/tests/unit/**/*.spec.(js|jsx|ts|tsx)|**/__tests__/*.(js|jsx|ts|tsx)'
  ],
  testURL: 'http://localhost/',
  watchPlugins: [
    'jest-watch-typeahead/filename',
    'jest-watch-typeahead/testname'
  ]
}
