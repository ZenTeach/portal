/* eslint-disable indent */
module.exports = {
  chainWebpack: config => {
    config.module.rule('eslint').use('eslint-loader')
    // svg loader
    config.module
      .rule('inline-svgo-loader')
      .test(/\.svg$/)
        .oneOf('inline')
        .resourceQuery(/^\?vue-template/)
        .use('vue-template-loader')
          .loader('vue-template-loader')
          .options({
            functional: true
          })
          .end()
        .end()

    config.module
      .rule('external-svgo-loader')
        .test(/\.svg$/)
          .oneOf('external')
            .use('file-loader')
              .loader('file-loader')
              .options({
                name: 'assets/svgs/[name].[ext]?[hash]'
              })
            .end()
          .end()

    config.module
      .rule('svgo-loader')
      .test(/\.svg$/)
        .use('svgo-loader')
        .loader('svgo-loader')
        .options({
          plugins: [
            { removeViewBox: false },
            { removeDimensions: true }]
          })
        .end()
      .end()
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
