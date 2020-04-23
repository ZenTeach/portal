module.exports = {
  chainWebpack: config => {
    config.module.rule('eslint').use('eslint-loader')
  },
  configureWebpack: {
    entry: {
      app: './main.js'
    },
    resolve: {
      alias: require('./aliases.config').webpack
    }
  }
}
