// http://jamesknelson.com/using-es6-in-the-browser-with-babel-6-and-webpack/

var path = require('path');
var webpack = require('webpack');

module.exports = {
  entry: [
    'babel-polyfill',
    './src/app'
  ],
  
  output: {
    path: path.join(__dirname, 'dist'),
    filename: 'bundle.js'
  },

  plugins: [
    new webpack.ProvidePlugin({
      $: 'jquery',
      jQuery: 'jquery',
      gridster: 'gridster'
    })
  ],

  module: {
    loaders: [
      {
        test: /\.(js|jsx)$/,
        loader: 'babel-loader', // 'babel-loader' is also a legal name to reference 
        include: [
          path.join(__dirname, 'src'),
          path.join(__dirname, 'test')
        ],
        exclude: /(node_modules|bower_components)/,
        query: {
          plugins: ['transform-runtime'],
          presets: ['react', 'es2015']
        }
      },
      { test: /\.css$/, loader: 'style-loader!css-loader' }, 
      { test: /\.eot(\?v=\d+\.\d+\.\d+)?$/, loader: "file-loader" },
      { test: /\.(woff|woff2)$/, loader:"url-loader?prefix=font/&limit=5000" },
      { test: /\.ttf(\?v=\d+\.\d+\.\d+)?$/, loader: "url-loader?limit=10000&mimetype=application/octet-stream" },
      { test: /\.svg(\?v=\d+\.\d+\.\d+)?$/, loader: "url-loader?limit=10000&mimetype=image/svg+xml" }
    ]
  }
};
