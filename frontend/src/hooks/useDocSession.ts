import { useState, useEffect, useRef, useCallback } from "react"
import { startSession, stopSession, getStatus, getResult, getNotionStatus } from "@/lib/api"

export type Phase = "idle" | "recording" | "generating" | "ready"

export interface DocSessionState {
  phase: Phase
  notionUrl: string
  error: string | null
  notionReady: boolean | null
  startRecording: () => Promise<void>
  stopRecording: () => Promise<void>
  reset: () => void
}

export function useDocSession(): DocSessionState {
  const [phase, setPhase] = useState<Phase>("idle")
  const [notionUrl, setNotionUrl] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [notionReady, setNotionReady] = useState<boolean | null>(null)
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    getNotionStatus()
      .then(({ configured }) => setNotionReady(configured))
      .catch(() => setNotionReady(false))
  }, [])

  useEffect(() => {
    if (phase !== "generating") return

    pollingRef.current = setInterval(async () => {
      try {
        const { state } = await getStatus()
        if (state === "ready") {
          clearInterval(pollingRef.current!)
          const result = await getResult()
          setNotionUrl(result.notion_url)
          setPhase("ready")
        }
      } catch (err) {
        clearInterval(pollingRef.current!)
        setError(err instanceof Error ? err.message : "Unknown error")
        setPhase("idle")
      }
    }, 2000)

    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current)
    }
  }, [phase])

  const startRecording = useCallback(async () => {
    setError(null)
    try {
      await startSession()
      setPhase("recording")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start session")
    }
  }, [])

  const stopRecording = useCallback(async () => {
    try {
      await stopSession()
      setPhase("generating")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to stop session")
    }
  }, [])

  const reset = useCallback(() => {
    if (pollingRef.current) clearInterval(pollingRef.current)
    setPhase("idle")
    setNotionUrl("")
    setError(null)
  }, [])

  return { phase, notionUrl, error, notionReady, startRecording, stopRecording, reset }
}
