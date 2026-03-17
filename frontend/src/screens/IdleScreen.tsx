import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"

interface Props {
  startRecording: () => Promise<void>
  error: string | null
}

export function IdleScreen({ startRecording, error }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.25 }}
      style={{ display: "flex", flexDirection: "column", gap: 12, width: "100%" }}
    >
      <p style={{
        fontFamily: "'Instrument Serif', serif",
        fontSize: 20,
        color: "#FAFAFA",
        margin: 0,
        lineHeight: 1.2,
      }}>
        Doc Agent
      </p>
      <p style={{ fontSize: 13, color: "#71717A", margin: 0 }}>
        Record your screen. Get documentation.
      </p>

      {error && (
        <p style={{
          fontSize: 12,
          color: "#F87171",
          margin: 0,
          padding: "6px 10px",
          background: "rgba(248,113,113,0.08)",
          borderRadius: 6,
          border: "1px solid rgba(248,113,113,0.2)",
        }}>
          {error}
        </p>
      )}

      <Button
        onClick={startRecording}
        style={{
          width: "100%",
          background: "#F59E0B",
          color: "#0D0D0F",
          fontWeight: 600,
          fontSize: 14,
          height: 40,
          borderRadius: 8,
          border: "none",
          cursor: "pointer",
          marginTop: 4,
        }}
      >
        Start Documentation Mode
      </Button>
    </motion.div>
  )
}
