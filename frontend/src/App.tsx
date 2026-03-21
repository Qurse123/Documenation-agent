import { useEffect, useState } from "react"

import { useDocSession } from "@/hooks/useDocSession"

type WidgetPhase = "idle" | "recording" | "generating" | "done"

const NOTION_ICON = (
  <svg
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M4.459 4.208c.746.606 1.026.56 2.428.466l13.215-.793c.28 0 .047-.28-.046-.326L17.86 1.968c-.42-.326-.981-.7-2.055-.607L3.01 2.295c-.466.046-.56.28-.374.466l1.823 1.447zm.793 3.08v13.904c0 .747.373 1.027 1.214.98l14.523-.84c.841-.046.935-.56.935-1.167V6.354c0-.606-.233-.933-.748-.887l-15.177.887c-.56.047-.747.327-.747.933zm14.337.745c.093.42 0 .84-.42.888l-.7.14v10.264c-.608.327-1.168.514-1.635.514-.748 0-.935-.234-1.495-.933l-4.577-7.186v6.952L12.21 19s0 .84-1.168.84l-3.222.186c-.093-.186 0-.653.327-.746l.84-.233V9.854L7.822 9.76c-.094-.42.14-1.026.793-1.073l3.456-.233 4.764 7.279v-6.44l-1.215-.14c-.093-.514.28-.887.747-.933l3.222-.187z"
      fill="currentColor"
    />
  </svg>
)

function RecordingDot() {
  return (
    <span
      style={{
        position: "relative",
        display: "inline-flex",
        width: 10,
        height: 10,
        flexShrink: 0,
      }}
    >
      <span
        style={{
          position: "absolute",
          display: "inline-flex",
          width: "100%",
          height: "100%",
          borderRadius: "50%",
          background: "#f87171",
          opacity: 0.6,
          animation: "ping 1s cubic-bezier(0,0,0.2,1) infinite",
        }}
      />
      <span
        style={{
          position: "relative",
          display: "inline-flex",
          width: 10,
          height: 10,
          borderRadius: "50%",
          background: "#ef4444",
        }}
      />
      <style>{`@keyframes ping { 75%,100%{transform:scale(2);opacity:0} }`}</style>
    </span>
  )
}

function ElapsedTimer() {
  const [seconds, setSeconds] = useState(0)
  useEffect(() => {
    const interval = setInterval(() => setSeconds((s) => s + 1), 1000)
    return () => clearInterval(interval)
  }, [])

  const mm = String(Math.floor(seconds / 60)).padStart(2, "0")
  const ss = String(seconds % 60).padStart(2, "0")
  return (
    <span
      style={{
        fontFamily: "monospace",
        color: "#f87171",
        fontSize: 11,
        fontWeight: 600,
        letterSpacing: "0.08em",
      }}
    >
      {mm}:{ss}
    </span>
  )
}

const GENERATION_STEPS = [
  "Analyzing session...",
  "Extracting actions...",
  "Structuring docs...",
  "Formatting for Notion...",
  "Finalizing...",
]

const WIDGET_WIDTHS: Record<WidgetPhase, number> = {
  idle: 220,
  recording: 224,
  generating: 248,
  done: 240,
}

function mapPhase(phase: ReturnType<typeof useDocSession>["phase"]): WidgetPhase {
  if (phase === "ready") return "done"
  return phase
}

export default function App() {
  const {
    phase,
    notionUrl,
    error,
    notionReady,
    notionOAuthConfigured,
    connectNotion,
    startRecording,
    stopRecording,
    reset,
  } = useDocSession()
  const [progress, setProgress] = useState(0)
  const [stepIndex, setStepIndex] = useState(0)
  const [visible, setVisible] = useState(true)
  const [mounted, setMounted] = useState(false)

  const widgetPhase = mapPhase(phase)

  useEffect(() => {
    const timeout = setTimeout(() => setMounted(true), 80)
    return () => clearTimeout(timeout)
  }, [])

  useEffect(() => {
    if (widgetPhase !== "generating") return

    const totalDuration = 4000
    const tickInterval = 50
    const ticks = totalDuration / tickInterval
    let tick = 0

    const interval = setInterval(() => {
      tick += 1
      const raw = tick / ticks
      const eased =
        raw < 0.5 ? 4 * raw * raw * raw : 1 - Math.pow(-2 * raw + 2, 3) / 2
      setProgress(Math.min(99, Math.round(eased * 100)))
      setStepIndex(
        Math.min(Math.floor((tick / ticks) * GENERATION_STEPS.length), GENERATION_STEPS.length - 1),
      )

      if (tick >= ticks) {
        clearInterval(interval)
      }
    }, tickInterval)

    return () => clearInterval(interval)
  }, [widgetPhase])

  const panel: React.CSSProperties = {
    position: "relative",
    width: WIDGET_WIDTHS[widgetPhase],
    height: "100vh",
    background: "rgba(12,12,14,0.98)",
    border: "1px solid rgba(255,255,255,0.12)",
    borderRadius: 16,
    boxShadow: "0 10px 24px rgba(0,0,0,0.45)",
    transition: "width 0.3s cubic-bezier(0.4,0,0.2,1), opacity 0.35s ease, transform 0.35s ease",
    opacity: mounted ? 1 : 0,
    transform: mounted ? "translateY(0) scale(1)" : "translateY(8px) scale(0.97)",
    display: "flex",
    flexDirection: "column",
    overflow: "hidden",
    userSelect: "none",
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  }

  const divider: React.CSSProperties = {
    height: 1,
    width: "100%",
    background: "rgba(255,255,255,0.06)",
  }

  if (!visible) {
    return (
      <button
        onClick={() => setVisible(true)}
        style={{
          position: "relative",
          display: "flex",
          alignItems: "center",
          gap: 6,
          padding: "6px 12px",
          borderRadius: 999,
          fontSize: 11,
          fontWeight: 500,
          color: "rgba(255,255,255,0.6)",
          background: "rgba(255,255,255,0.08)",
          border: "1px solid rgba(255,255,255,0.12)",
          cursor: "pointer",
        }}
      >
        Doc Mode
      </button>
    )
  }

  return (
    <div style={panel}>
      <div
        style={{
          height: 22,
          // @ts-expect-error Electron-specific CSS property
          WebkitAppRegion: "drag",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <div
          style={{
            width: 28,
            height: 3,
            borderRadius: 2,
            background: "rgba(255,255,255,0.25)",
          }}
        />
      </div>

      <div
        style={{
          padding: 12,
          display: "flex",
          flexDirection: "column",
          gap: 10,
          flex: 1,
          // @ts-expect-error Electron-specific CSS property
          WebkitAppRegion: "no-drag",
        }}
      >
        {widgetPhase === "idle" && (
          <>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <span
                style={{
                  fontSize: 10,
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.12em",
                  color: "rgba(255,255,255,0.28)",
                }}
              >
                Doc Mode
              </span>
              <button
                onClick={() => setVisible(false)}
                style={{
                  width: 20,
                  height: 20,
                  borderRadius: 6,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "rgba(255,255,255,0.25)",
                  background: "rgba(255,255,255,0.05)",
                  border: "none",
                  cursor: "pointer",
                }}
              >
                <svg width="8" height="8" viewBox="0 0 8 8" fill="none">
                  <path
                    d="M1 1L7 7M7 1L1 7"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                  />
                </svg>
              </button>
            </div>

            <p style={{ fontSize: 13, color: "#B0B0B5", margin: 0 }}>
              Record your screen. Get documentation.
            </p>

            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <div
                style={{
                  width: 7,
                  height: 7,
                  borderRadius: "50%",
                  background:
                    notionReady === null ? "#C0C0C5" : notionReady ? "#22C55E" : "#EF4444",
                  flexShrink: 0,
                }}
              />
              <span
                style={{
                  fontSize: 12,
                  color: "#888888",
                  fontFamily: "'DM Mono', monospace",
                }}
              >
                {notionReady === null
                  ? "Checking Notion..."
                  : notionReady
                    ? "Notion ready"
                    : notionOAuthConfigured
                      ? "Connect Notion to continue"
                      : "Set OAuth env vars in .env"}
              </span>
            </div>

            {error && (
              <p
                style={{
                  fontSize: 12,
                  color: "#F87171",
                  margin: 0,
                  padding: "6px 10px",
                  background: "rgba(248,113,113,0.08)",
                  borderRadius: 6,
                  border: "1px solid rgba(248,113,113,0.2)",
                }}
              >
                {error}
              </p>
            )}

            {!notionReady && notionOAuthConfigured && (
              <button
                onClick={connectNotion}
                style={{
                  width: "100%",
                  padding: "8px 0",
                  borderRadius: 10,
                  fontSize: 12,
                  fontWeight: 600,
                  color: "#FFFFFF",
                  border: "1px solid rgba(255,255,255,0.2)",
                  cursor: "pointer",
                  background: "rgba(255,255,255,0.08)",
                }}
              >
                Connect Notion
              </button>
            )}

            <button
              onClick={startRecording}
              disabled={notionReady !== true}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: 7,
                width: "100%",
                padding: "8px 0",
                borderRadius: 12,
                fontSize: 12,
                fontWeight: 600,
                color: notionReady === true ? "#FFFFFF" : "#AAAAAA",
                border: "none",
                cursor: notionReady === true ? "pointer" : "not-allowed",
                background:
                  notionReady === true
                    ? "linear-gradient(135deg, #7c3aed, #6d28d9)"
                    : "#E5E5E5",
              }}
            >
              <span
                style={{
                  width: 7,
                  height: 7,
                  borderRadius: "50%",
                  background: notionReady === true ? "rgba(255,255,255,0.7)" : "#C0C0C5",
                  display: "inline-block",
                }}
              />
              Start Documentation Mode
            </button>
          </>
        )}

        {widgetPhase === "recording" && (
          <>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <RecordingDot />
                <span
                  style={{
                    fontSize: 10,
                    fontWeight: 700,
                    textTransform: "uppercase",
                    letterSpacing: "0.12em",
                    color: "#f87171",
                  }}
                >
                  Recording
                </span>
              </div>
                <ElapsedTimer />
            </div>
            <div style={divider} />
            <button
              onClick={stopRecording}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: 8,
                width: "100%",
                padding: "8px 0",
                borderRadius: 12,
                fontSize: 12,
                fontWeight: 600,
                color: "rgba(255,255,255,0.9)",
                cursor: "pointer",
                background: "rgba(239,68,68,0.15)",
                border: "1px solid rgba(239,68,68,0.3)",
              }}
            >
              <span
                style={{
                  width: 10,
                  height: 10,
                  borderRadius: 3,
                  background: "rgba(239,68,68,0.9)",
                  display: "inline-block",
                }}
              />
              End Documentation Mode
            </button>
          </>
        )}

        {widgetPhase === "generating" && (
          <>
            <style>{`@keyframes spin { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }`}</style>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <svg
                  width="10"
                  height="10"
                  viewBox="0 0 24 24"
                  fill="none"
                  style={{ color: "#a78bfa", animation: "spin 2s linear infinite" }}
                >
                  <path
                    d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                  />
                </svg>
                <span
                  style={{
                    fontSize: 10,
                    fontWeight: 700,
                    textTransform: "uppercase",
                    letterSpacing: "0.12em",
                    color: "#a78bfa",
                  }}
                >
                  Generating
                </span>
              </div>
              <span
                style={{
                  fontSize: 10,
                  fontFamily: "monospace",
                  fontWeight: 600,
                  color: "#a78bfa",
                }}
              >
                {progress}%
              </span>
            </div>
            <div
              style={{
                width: "100%",
                borderRadius: 999,
                overflow: "hidden",
                height: 3,
                background: "rgba(255,255,255,0.07)",
              }}
            >
              <div
                style={{
                  height: "100%",
                  borderRadius: 999,
                  width: `${progress}%`,
                  background: "linear-gradient(90deg, #7c3aed, #a78bfa)",
                  transition: "width 0.3s ease",
                }}
              />
            </div>
            <p
              style={{
                fontSize: 10,
                color: "rgba(255,255,255,0.3)",
                margin: 0,
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
            >
              {GENERATION_STEPS[stepIndex]}
            </p>
          </>
        )}

        {widgetPhase === "done" && (
          <>
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <div
                style={{
                  width: 16,
                  height: 16,
                  borderRadius: "50%",
                  background: "rgba(124,58,237,0.25)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flexShrink: 0,
                }}
              >
                <svg width="8" height="8" viewBox="0 0 12 12" fill="none">
                  <polyline
                    points="10 3 4.5 8.5 2 6"
                    stroke="#a78bfa"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
              <span
                style={{
                  fontSize: 10,
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.12em",
                  color: "#c4b5fd",
                }}
              >
                Docs ready
              </span>
            </div>
            <div style={divider} />
            <a
              href={notionUrl || "#"}
              target={notionUrl ? "_blank" : undefined}
              rel={notionUrl ? "noreferrer" : undefined}
              onClick={(e) => {
                if (!notionUrl) e.preventDefault()
              }}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: 7,
                width: "100%",
                padding: "8px 0",
                borderRadius: 12,
                fontSize: 12,
                fontWeight: 600,
                color: "#fff",
                textDecoration: "none",
                background: "rgba(255,255,255,0.08)",
                border: "1px solid rgba(255,255,255,0.12)",
                cursor: notionUrl ? "pointer" : "not-allowed",
              }}
            >
              {NOTION_ICON}
              View in Notion
            </a>
            <button
              onClick={reset}
              style={{
                fontSize: 10,
                color: "rgba(255,255,255,0.4)",
                background: "none",
                border: "none",
                cursor: "pointer",
                textAlign: "center",
                padding: "2px 0",
              }}
            >
              Start new session
            </button>
          </>
        )}
      </div>
    </div>
  )
}
