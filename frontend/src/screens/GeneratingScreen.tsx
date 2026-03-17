import { useState, useEffect } from "react"
import { motion } from "framer-motion"

export function GeneratingScreen() {
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const t = setInterval(() => {
      setProgress(p => p >= 90 ? p : p + Math.random() * 5)
    }, 600)
    return () => clearInterval(t)
  }, [])

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.25 }}
      style={{ display: "flex", flexDirection: "column", gap: 16, width: "100%" }}
    >
      <p style={{
        fontFamily: "'Instrument Serif', serif",
        fontSize: 20,
        color: "#FAFAFA",
        margin: 0,
      }}>
        Building your docs…
      </p>

      <div style={{ height: 2, background: "#1f1f23", borderRadius: 2, overflow: "hidden" }}>
        <motion.div
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          style={{ height: "100%", background: "#F59E0B", borderRadius: 2 }}
        />
      </div>

      <p style={{ fontSize: 12, color: "#3f3f46", margin: 0, fontFamily: "'DM Mono', monospace" }}>
        This may take a moment…
      </p>
    </motion.div>
  )
}
