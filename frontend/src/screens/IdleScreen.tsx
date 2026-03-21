import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"

interface Props {
  startRecording: () => Promise<void>
  error: string | null
  notionReady: boolean | null
}

function NotionStatusRow({ notionReady }: { notionReady: boolean | null }) {
  const dot =
    notionReady === null ? "#C0C0C5" : notionReady ? "#22C55E" : "#EF4444"
  const label =
    notionReady === null
      ? "Checking Notion…"
      : notionReady
      ? "Notion ready"
      : "Configure Notion OAuth in .env"

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
      <div style={{ width: 7, height: 7, borderRadius: "50%", background: dot, flexShrink: 0 }} />
      <span style={{ fontSize: 12, color: "#888888", fontFamily: "'DM Mono', monospace" }}>
        {label}
      </span>
    </div>
  )
}

export function IdleScreen({ startRecording, error, notionReady }: Props) {
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
        color: "#111111",
        margin: 0,
        lineHeight: 1.2,
      }}>
        Doc Agent
      </p>
      <p style={{ fontSize: 13, color: "#666666", margin: 0 }}>
        Record your screen. Get documentation.
      </p>

      <NotionStatusRow notionReady={notionReady} />

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
        disabled={notionReady !== true}
        style={{
          width: "100%",
          background: notionReady === true ? "#F59E0B" : "#E5E5E5",
          color: notionReady === true ? "#0D0D0F" : "#AAAAAA",
          fontWeight: 600,
          fontSize: 14,
          height: 40,
          borderRadius: 8,
          border: "none",
          cursor: notionReady === true ? "pointer" : "not-allowed",
          marginTop: 4,
        }}
      >
        Start Documentation Mode
      </Button>
    </motion.div>
  )
}
