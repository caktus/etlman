const path = require('path');
const MonacoWebpackPlugin = require('monaco-editor-webpack-plugin');


module.exports = {
	entry: './index.js',
	mode: 'development',
	output: {
		path: path.resolve(__dirname, 'etlman/static/js'),
		filename: 'app.js'
	},
	module: {
		rules: [
			{
				test: /\.css$/,
				use: ['style-loader', 'css-loader']
			},
            {
				test: /\.ttf$/,
				type: 'asset/resource'
			}
		]
	},
	plugins: [new MonacoWebpackPlugin()]
}
