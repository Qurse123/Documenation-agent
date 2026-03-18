import { AnimatePresence } from "framer-motion"
import { useDocSession } from "@/hooks/useDocSession"
import { IdleScreen } from "@/screens/IdleScreen"
import { RecordingScreen } from "@/screens/RecordingScreen"
import { GeneratingScreen } from "@/screens/GeneratingScreen"
import { ReadyScreen } from "@/screens/ReadyScreen"

export default function App() {
  const { phase, notionUrl, error, notionReady, startRecording, stopRecording, reset } = useDocSession()

  return (
    <div style={{
      minHeight: "100vh",
      display: "flex",
      alignItems: "stretch",
    }}>
      <div style={{
        width: "100%",
        background: "#F5F5F5",
        borderRadius: 14,
        overflow: "hidden",
      }}>
        {/* Drag handle — grab here to move the window */}
        <div style={{
          height: 28,
          // @ts-expect-error Electron-specific CSS property
          WebkitAppRegion: "drag",
          cursor: "grab",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}>
          <div style={{
            width: 32,
            height: 3,
            borderRadius: 2,
            background: "#C0C0C5",
          }} />
        </div>
        <div style={{ padding: "20px 20px 24px", // @ts-expect-error Electron-specific CSS property
          WebkitAppRegion: "no-drag" }}>
        <AnimatePresence mode="wait">
          {phase === "idle" && (
            <IdleScreen key="idle" startRecording={startRecording} error={error} notionReady={notionReady} />
          )}
          {phase === "recording" && (
            <RecordingScreen key="recording" stopRecording={stopRecording} />
          )}
          {phase === "generating" && (
            <GeneratingScreen key="generating" />
          )}
          {phase === "ready" && (
            <ReadyScreen key="ready" notionUrl={notionUrl} reset={reset} />
          )}
        </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
