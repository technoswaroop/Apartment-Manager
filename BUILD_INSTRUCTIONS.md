# Building Desktop App

## Prerequisites
1. Install Node.js (version 16 or higher)
2. Clone this project to your laptop

## Setup Instructions

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Add Electron dependencies:**
   ```bash
   npm install --save-dev electron electron-builder concurrently wait-on
   ```

3. **Update package.json** - Add these scripts to your package.json:
   ```json
   {
     "main": "electron/main.js",
     "scripts": {
       "electron": "concurrently \"npm run dev\" \"wait-on http://localhost:8080 && electron .\"",
       "electron:dev": "NODE_ENV=development electron .",
       "electron:build": "npm run build && electron-builder",
       "electron:dist": "npm run build && electron-builder --publish=never"
     }
   }
   ```

## Running the Desktop App

### Development Mode
```bash
npm run electron
```
This will start both the web server and Electron app.

### Building Executable

1. **Build for Windows (.exe):**
   ```bash
   npm run electron:dist
   ```

2. **Build for specific platform:**
   ```bash
   # Windows
   npx electron-builder --win
   
   # macOS
   npx electron-builder --mac
   
   # Linux
   npx electron-builder --linux
   ```

## Output
- The executable will be created in the `dist-electron` folder
- For Windows: Look for the `.exe` installer file
- Double-click to install and run

## Features
- ✅ Offline capable desktop app
- ✅ Native Windows/Mac/Linux support
- ✅ Auto-updater ready
- ✅ Professional installer
- ✅ Desktop shortcuts
- ✅ System tray integration ready

## File Size
Expect the installer to be around 150-200MB (includes Chromium runtime).

## Troubleshooting
If you encounter build errors:
1. Clear node_modules: `rm -rf node_modules && npm install`
2. Clear electron cache: `npx electron-builder install-app-deps`
3. Try building with verbose output: `DEBUG=electron-builder npm run electron:dist`