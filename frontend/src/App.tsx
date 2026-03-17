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
        padding: "24px 20px",
      }}>
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
  )
}
