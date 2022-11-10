const path = require('path');
const MonacoWebpackPlugin = require('monaco-editor-webpack-plugin');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");

module.exports = {
	entry: './index.js',
	mode: 'development',
	output: {
		path: path.resolve(__dirname, 'etlman/static'),
		filename: 'js/app.js',
	},
	optimization: {
		minimizer: [
			new CssMinimizerPlugin(),
		  ],
		minimize: true,
		splitChunks: {
		  cacheGroups: {
			styles: {
			  name: "styles",
			  type: "css/mini-extract",
			  chunks: "all",
			  enforce: true,
			},
		  },
		},
	  },
	module: {
		rules: [
			{
				test: /\.css$/,
				use: [MiniCssExtractPlugin.loader, "css-loader"],
				},
            {
				test: /\.ttf$/,
				type: 'asset/resource'
			}
		]
	},
	plugins: [
		new MonacoWebpackPlugin(),
		new MiniCssExtractPlugin({
			filename: "css/project.css",
		  }),
	]
}
