const { app, BrowserWindow, screen, shell } = require("electron")

function createWindow() {
  const { x, y, width } = screen.getPrimaryDisplay().workArea
  const WINDOW_WIDTH = 248
  const WINDOW_HEIGHT = 240
  const EDGE_MARGIN = -24

  const win = new BrowserWindow({
    width: WINDOW_WIDTH,
    height: WINDOW_HEIGHT,
    x: x + width - WINDOW_WIDTH - EDGE_MARGIN,
    y: y + EDGE_MARGIN,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: true,
    minWidth: 248,
    minHeight: 160,
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
