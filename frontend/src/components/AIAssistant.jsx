import { useEffect, useMemo, useRef, useState } from "react"
import { FiArrowRight, FiMessageSquare, FiRefreshCw, FiSend, FiX, FiZap } from "react-icons/fi"
import { useNavigate } from "react-router-dom"

import api, { auth, endpoints, extractApiError } from "../services/api"

const starterPromptsByRole = {
  student: [
    "Show my attendance",
    "Summarize my recent results",
    "Show my timetable help",
  ],
  teacher: [
    "Which students have low attendance?",
    "Give me performance insights",
    "Generate test questions",
  ],
  admin: [
    "Generate fee summary",
    "Show admission analytics",
    "Draft an announcement",
  ],
  super_admin: [
    "Give me a platform summary",
    "Show institution-level trends",
    "Summarize growth signals",
  ],
}

function mapHistoryToMessages(history) {
  return history.flatMap((item) => [
    {
      id: `user-${item.id}`,
      sender: "user",
      text: item.user_message,
      timestamp: item.created_at,
    },
    {
      id: `assistant-${item.id}`,
      sender: "assistant",
      text: item.assistant_message,
      timestamp: item.created_at,
      provider: item.provider,
    },
  ])
}

function AIAssistant() {
  const navigate = useNavigate()
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [briefing, setBriefing] = useState(null)
  const [loadingHistory, setLoadingHistory] = useState(false)
  const [loadingBriefing, setLoadingBriefing] = useState(false)
  const [historyLoaded, setHistoryLoaded] = useState(false)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState("")
  const [briefingError, setBriefingError] = useState("")
  const messageListRef = useRef(null)

  const role = auth.getRole() || "student"
  const institutionName = auth.getInstitutionShortName() || auth.getInstitutionName() || "Campus"
  const starterPrompts = useMemo(
    () => briefing?.suggested_prompts || starterPromptsByRole[role] || starterPromptsByRole.admin,
    [briefing?.suggested_prompts, role],
  )

  useEffect(() => {
    if (!messageListRef.current) {
      return
    }
    messageListRef.current.scrollTop = messageListRef.current.scrollHeight
  }, [messages, isOpen, sending])

  useEffect(() => {
    if (!isOpen || historyLoaded) {
      return
    }

    let active = true
    setLoadingHistory(true)
    setError("")
    api
      .get(endpoints.aiChat)
      .then((response) => {
        if (!active) {
          return
        }
        setMessages(mapHistoryToMessages(response.data.history || []))
        setHistoryLoaded(true)
      })
      .catch((err) => {
        if (!active) {
          return
        }
        setError(extractApiError(err, "Unable to load AI chat history"))
      })
      .finally(() => {
        if (active) {
          setLoadingHistory(false)
        }
      })

    return () => {
      active = false
    }
  }, [historyLoaded, isOpen])

  const loadBriefing = async () => {
    setLoadingBriefing(true)
    setBriefingError("")
    try {
      const response = await api.get(endpoints.aiBriefing)
      setBriefing(response.data)
    } catch (err) {
      setBriefingError(extractApiError(err, "Unable to load automation brief"))
    } finally {
      setLoadingBriefing(false)
    }
  }

  const handleSend = async (nextMessage) => {
    const text = (nextMessage ?? input).trim()
    if (!text || sending) {
      return
    }

    const tempId = `pending-${Date.now()}`
    setSending(true)
    setError("")
    setInput("")
    setMessages((current) => [
      ...current,
      { id: `${tempId}-user`, sender: "user", text },
      { id: `${tempId}-assistant`, sender: "assistant", text: "", typing: true },
    ])

    try {
      const response = await api.post(endpoints.aiChat, { message: text })
      const nextMessages = mapHistoryToMessages([response.data])
      setMessages((current) => [
        ...current.filter((item) => !item.id.startsWith(tempId)),
        ...nextMessages,
      ])
      setHistoryLoaded(true)
    } catch (err) {
      setMessages((current) => current.filter((item) => !item.id.startsWith(tempId)))
      setError(extractApiError(err, "Unable to reach the AI assistant"))
    } finally {
      setSending(false)
    }
  }

  return (
    <>
      <button
        type="button"
        className={`ai-chat-fab ${isOpen ? "open" : ""}`}
        onClick={() => setIsOpen((current) => !current)}
        aria-label={isOpen ? "Close AI assistant" : "Open AI assistant"}
      >
        {isOpen ? <FiX size={22} /> : <FiMessageSquare size={22} />}
      </button>

      {isOpen ? (
        <section className="ai-chat-panel" aria-label="AI assistant">
          <header className="ai-chat-header">
            <div>
              <p className="eyebrow">AI Assistant</p>
              <h3>{institutionName} Copilot</h3>
            </div>
            <span className="ai-chat-role">{role.replace("_", " ")}</span>
          </header>

          <div className="ai-chat-prompts">
            {starterPrompts.map((prompt) => (
              <button
                key={prompt}
                type="button"
                className="ai-chat-chip"
                onClick={() => handleSend(prompt)}
                disabled={sending}
              >
                <FiZap size={14} />
                <span>{prompt}</span>
              </button>
            ))}
          </div>

          <div className="ai-briefing-toolbar">
            <button
              type="button"
              className="ai-briefing-trigger"
              onClick={loadBriefing}
              disabled={loadingBriefing}
            >
              {loadingBriefing ? <FiRefreshCw size={14} className="ai-spin" /> : <FiZap size={14} />}
              <span>{briefing ? "Refresh full brief" : "Run full brief"}</span>
            </button>
          </div>

          <div className="ai-chat-messages" ref={messageListRef}>
            {briefing ? (
              <section className="ai-briefing-card">
                <div className="ai-briefing-heading">
                  <div>
                    <p className="eyebrow">One Click Automation</p>
                    <h4>{briefing.headline}</h4>
                  </div>
                </div>
                <p className="ai-briefing-summary">{briefing.summary}</p>
                <div className="ai-briefing-sections">
                  {briefing.sections.map((section) => (
                    <article key={section.title} className="ai-briefing-section">
                      <div className="ai-briefing-section-header">
                        <h5>{section.title}</h5>
                        {section.action ? (
                          <button
                            type="button"
                            className="ai-briefing-link"
                            onClick={() => navigate(section.action.path)}
                          >
                            <span>{section.action.label}</span>
                            <FiArrowRight size={14} />
                          </button>
                        ) : null}
                      </div>
                      <dl className="ai-briefing-metrics">
                        {section.items.map((item) => (
                          <div key={`${section.title}-${item.label}`}>
                            <dt>{item.label}</dt>
                            <dd>{item.value}</dd>
                          </div>
                        ))}
                      </dl>
                    </article>
                  ))}
                </div>
              </section>
            ) : null}

            {briefingError ? <p className="error-text ai-chat-error">{briefingError}</p> : null}

            {loadingHistory ? (
              <div className="ai-chat-empty">
                <div className="ai-typing-dots">
                  <span />
                  <span />
                  <span />
                </div>
                <p>Loading chat history...</p>
              </div>
            ) : null}

            {!loadingHistory && messages.length === 0 ? (
              <div className="ai-chat-empty">
                <p>
                  {briefing
                    ? "Ask follow-up questions or use the quick links above."
                    : "Run the full brief or ask about attendance, results, analytics, admissions, or fees."}
                </p>
              </div>
            ) : null}

            {messages.map((message) => (
              <article
                key={message.id}
                className={`ai-chat-bubble ${message.sender === "user" ? "user" : "assistant"}`}
              >
                <span className="ai-chat-author">
                  {message.sender === "user" ? "You" : "AI"}
                </span>
                {message.typing ? (
                  <div className="ai-typing-dots">
                    <span />
                    <span />
                    <span />
                  </div>
                ) : (
                  <p>{message.text}</p>
                )}
              </article>
            ))}
          </div>

          {error ? <p className="error-text ai-chat-error">{error}</p> : null}

          <form
            className="ai-chat-form"
            onSubmit={(event) => {
              event.preventDefault()
              handleSend()
            }}
          >
            <textarea
              rows={2}
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask your AI assistant something useful..."
              disabled={sending}
            />
            <button type="submit" className="button ai-chat-submit" disabled={sending || !input.trim()}>
              <FiSend size={16} />
            </button>
          </form>
        </section>
      ) : null}
    </>
  )
}

export default AIAssistant
