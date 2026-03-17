const { app, BrowserWindow, screen, shell } = require("electron")

function createWindow() {
  const { width } = screen.getPrimaryDisplay().workAreaSize

  const win = new BrowserWindow({
    width: 340,
    height: 240,
    x: Math.round(width / 2 - 170),
    y: 20,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: true,
    skipTaskbar: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  })

  win.setAlwaysOnTop(true, "screen-saver")

  // Open all window.open() calls in the system default browser
  win.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: "deny" }
  })

  const isDev = !app.isPackaged
  if (isDev) {
    win.loadURL("http://localhost:5173")
  } else {
    win.loadFile("dist/index.html")
  }
}

app.whenReady().then(createWindow)

app.on("window-all-closed", () => {
  app.quit()
})
