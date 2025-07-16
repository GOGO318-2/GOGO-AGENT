import { defineConfig } from 'vite';
    import react from '@vitejs/plugin-react';

    export default defineConfig({
      plugins: [react()],
      build: {
        outDir: 'dist', // 输出目录
      },
      root: __dirname, // 项目根目录
      publicDir: 'public', // 指定 public 目录
      // 显式设置入口（可选，但可解决问题）
      appType: 'custom', // 使用自定义入口
      build: {
        rollupOptions: {
          input: {
            main: './public/index.html', // 明确指定入口
          },
        },
      },
    });