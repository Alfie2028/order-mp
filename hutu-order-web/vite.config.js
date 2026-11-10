import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'
import fs from 'fs'
import path from 'path'

function copyDir(src, dest) {
  if (!fs.existsSync(src)) return
  fs.mkdirSync(dest, { recursive: true })
  const entries = fs.readdirSync(src, { withFileTypes: true })
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name)
    const destPath = path.join(dest, entry.name)
    if (entry.isDirectory()) {
      copyDir(srcPath, destPath)
    } else {
      fs.copyFileSync(srcPath, destPath)
    }
  }
}

function copyStaticPlugin() {
  return {
    name: 'copy-static-assets',
    closeBundle() {
      const outDir = process.env.UNI_OUTPUT_DIR
      if (outDir) {
        const staticSrc = path.resolve(__dirname, 'src/static')
        const staticDest = path.join(outDir, 'static')
        copyDir(staticSrc, staticDest)
      }
    }
  }
}

// https://vitejs.dev/config/
export default defineConfig({
  server: {
    port: 5174,
    host: '0.0.0.0',
  },
  plugins: [
    uni(),
    copyStaticPlugin(),
  ],
  css: {
    preprocessorOptions: {
      scss: {quietDeps: true}
    }
  }
})
