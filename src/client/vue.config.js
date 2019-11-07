module.exports = {
  configureWebpack: {
    entry: {
      app: "./main.js"
    },
    resolve: {
      alias: require("./aliases.config").webpack
    }
  }
};
