import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"

interface Props {
  stopRecording: () => Promise<void>
}

export function RecordingScreen({ stopRecording }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.25 }}
      style={{ display: "flex", flexDirection: "column", gap: 16, width: "100%" }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <motion.div
          animate={{ opacity: [1, 0.2, 1] }}
          transition={{ duration: 1.4, repeat: Infinity, ease: "easeInOut" }}
          style={{
            width: 8,
            height: 8,
            borderRadius: "50%",
            background: "#EF4444",
            flexShrink: 0,
          }}
        />
        <span style={{
          fontFamily: "'DM Mono', monospace",
          fontSize: 11,
          color: "#EF4444",
          letterSpacing: "0.1em",
          textTransform: "uppercase",
        }}>
          Recording
        </span>
      </div>

      <p style={{ fontSize: 13, color: "#71717A", margin: 0 }}>
        Perform the actions you want documented.
      </p>

      <Button
        onClick={stopRecording}
        style={{
          width: "100%",
          background: "transparent",
          color: "#FAFAFA",
          fontWeight: 500,
          fontSize: 14,
          height: 40,
          borderRadius: 8,
          border: "1px solid #2a2a2e",
          cursor: "pointer",
        }}
      >
        End Documentation Mode
      </Button>
    </motion.div>
  )
}
