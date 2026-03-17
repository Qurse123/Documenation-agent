import { AnimatePresence } from "framer-motion"
import { useDocSession } from "@/hooks/useDocSession"
import { IdleScreen } from "@/screens/IdleScreen"
import { RecordingScreen } from "@/screens/RecordingScreen"
import { GeneratingScreen } from "@/screens/GeneratingScreen"
import { ReadyScreen } from "@/screens/ReadyScreen"

export default function App() {
  const { phase, notionUrl, error, startRecording, stopRecording, reset } = useDocSession()

  return (
    <div style={{
      minHeight: "100vh",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: 16,
    }}>
      <div style={{
        width: "100%",
        maxWidth: 320,
        background: "#111113",
        border: "1px solid #1f1f23",
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
          borderBottom: "1px solid #1a1a1e",
        }}>
          <div style={{
            width: 32,
            height: 3,
            borderRadius: 2,
            background: "#2a2a2e",
          }} />
        </div>
        <div style={{ padding: "20px 20px 24px", // @ts-expect-error Electron-specific CSS property
          WebkitAppRegion: "no-drag" }}>
        <AnimatePresence mode="wait">
          {phase === "idle" && (
            <IdleScreen key="idle" startRecording={startRecording} error={error} />
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
