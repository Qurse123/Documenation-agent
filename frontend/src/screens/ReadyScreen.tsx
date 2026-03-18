import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"

interface Props {
  notionUrl: string
  reset: () => void
}

export function ReadyScreen({ notionUrl, reset }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.25 }}
      style={{ display: "flex", flexDirection: "column", gap: 16, width: "100%" }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 250, damping: 16 }}
          style={{
            width: 28,
            height: 28,
            borderRadius: "50%",
            background: "rgba(245,158,11,0.15)",
            border: "1px solid rgba(245,158,11,0.3)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0,
          }}
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <motion.path
              d="M2.5 7.5l3 3 6-6"
              stroke="#F59E0B"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 0.4, delay: 0.1 }}
            />
          </svg>
        </motion.div>
        <p style={{
          fontFamily: "'Instrument Serif', serif",
          fontSize: 18,
          color: "#111111",
          margin: 0,
        }}>
          Documentation ready
        </p>
      </div>

      <Button
        onClick={() => window.open(notionUrl, "_blank")}
        disabled={!notionUrl}
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
        }}
      >
        Check Notion
      </Button>

      <Button
        onClick={reset}
        variant="ghost"
        style={{
          width: "100%",
          color: "#888888",
          fontSize: 13,
          height: 36,
          borderRadius: 8,
          cursor: "pointer",
        }}
      >
        Start New Session
      </Button>
    </motion.div>
  )
}
