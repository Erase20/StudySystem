const { defineConfig } = require('@vue/cli-service')
const path = require('path')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://localhost:9090',
        changeOrigin: true,
        pathRewrite: {
          '^/api': ''
        }
      }
    }
  },
  // 构建优化配置
  configureWebpack: {
    // 配置webpack别名，简化导入路径
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
        '@components': path.resolve(__dirname, 'src/components'),
        '@views': path.resolve(__dirname, 'src/views'),
        '@api': path.resolve(__dirname, 'src/api'),
        '@utils': path.resolve(__dirname, 'src/utils'),
        '@assets': path.resolve(__dirname, 'src/assets'),
        '@store': path.resolve(__dirname, 'src/store')
      }
    },
    // 代码分割配置
    optimization: {
      splitChunks: {
        chunks: 'all',
        maxInitialRequests: Infinity,
        minSize: 20000,
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name(module) {
              const packageName = module.context.match(/[\\/]node_modules[\\/](.*?)([\\/]|$)/)[1]
              return `npm.${packageName.replace('@', '')}`
            }
          },
          common: {
            name: 'common',
            minChunks: 2,
            priority: -20,
            reuseExistingChunk: true
          }
        }
      }
    }
  },
  // 链式webpack配置
  chainWebpack: config =>{
    // 设置页面标题
    config.plugin('html')
        .tap(args => {
          args[0].title = "学习交流系统";
          return args;
        })
    
    // 优化图片处理
    config.module
      .rule('images')
      .use('url-loader')
      .loader('url-loader')
      .tap(options => {
        return {
          limit: 10240, // 10kb以下的图片使用base64
          fallback: {
            loader: 'file-loader',
            options: {
              name: 'img/[name].[hash:8].[ext]'
            }
          }
        }
      })
    
    // 优化生产环境构建
    if (process.env.NODE_ENV === 'production') {
      // 移除console和debugger
      config.optimization.minimizer('terser')
        .tap(args => {
          args[0].terserOptions.compress.drop_console = true
          args[0].terserOptions.compress.drop_debugger = true
          return args
        })
    }
  }
})
