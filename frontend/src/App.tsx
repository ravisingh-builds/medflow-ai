import { useEffect, useRef, useState } from "react";
import {
  Activity,
  Banknote,
  Bot,
  CalendarDays,
  CheckCircle2,
  Lock,
  Send,
  Smile,
  Sparkles,
  Stethoscope,
  User,
  UserRound,
  type LucideIcon,
} from "lucide-react";
import "./App.css";

type Message = {
  id: number;
  role: "agent" | "user";
  text: string;
  time: string;
};

type ExtractedFields = Record<string, string | null | undefined>;

type LeadResponse = {
  lead_id: string;
  conversation_id: string;
  question: string | null;
  field: string | null;
  workflow_id: string;
  extracted: ExtractedFields;
  priority: string;
  missing_fields: string[];
};

type ReplyResponse = {
  workflow_id: string;
  question: string | null;
  field: string | null;
  completed: boolean;
  extracted: ExtractedFields;
  priority: string;
  missing_fields: string[];
};

const FIELDS: { key: string; label: string; icon: LucideIcon }[] = [
  { key: "Patient Name", label: "Patient Name", icon: User },
  { key: "Date of Birth", label: "Date of Birth", icon: CalendarDays },
  { key: "Diagnosis", label: "Diagnosis", icon: Stethoscope },
  { key: "Referring Physician", label: "Referring Physician", icon: UserRound },
  { key: "Phone Number", label: "Phone Number", icon: Activity },
  { key: "Insurance Provider", label: "Insurance Provider", icon: Banknote },
];

function getTime() {
  return new Date().toLocaleTimeString([], {
    hour: "numeric",
    minute: "2-digit",
  });
}

const GREETING =
  "Hi there — let's get this referral started. Tell me who it's for and " +
  "the reason for referral, and I'll ask a few quick follow-ups along " +
  "the way.";

function App() {
  const idRef = useRef(0);

  function nextId() {
    idRef.current += 1;
    return idRef.current;
  }

  const [messages, setMessages] = useState<Message[]>([
    { id: nextId(), role: "agent", text: GREETING, time: getTime() },
  ]);

  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);

  const [started, setStarted] = useState(false);
  const [completed, setCompleted] = useState(false);

  const [workflowId, setWorkflowId] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);

  const [extracted, setExtracted] = useState<ExtractedFields>({});
  const [priority, setPriority] = useState<string | null>(null);
  const [missingFields, setMissingFields] = useState<string[]>([]);

  const messagesContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = messagesContainerRef.current;

    if (!container) {
      return;
    }

    container.scrollTo({
      top: container.scrollHeight,
      behavior: "smooth",
    });
  }, [messages.length, isSending]);

  function appendMessage(role: Message["role"], text: string) {
    setMessages((previous) => [
      ...previous,
      { id: nextId(), role, text, time: getTime() },
    ]);
  }

  async function handleSend() {
    const text = input.trim();

    if (!text || isSending || completed) {
      return;
    }

    setInput("");
    appendMessage("user", text);
    setIsSending(true);

    try {
      if (!started) {
        const response = await fetch("http://localhost:8000/leads", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ referral: text }),
        });

        const data: LeadResponse = await response.json();

        setWorkflowId(data.workflow_id);
        setConversationId(data.conversation_id);
        setExtracted(data.extracted ?? {});
        setPriority(data.priority ?? null);
        setMissingFields(data.missing_fields ?? []);
        setStarted(true);

        if (data.question) {
          appendMessage("agent", data.question);
        } else {
          setCompleted(true);
        }
      } else {
        if (!workflowId || !conversationId) {
          return;
        }

        const response = await fetch(
          "http://localhost:8000/conversation/reply",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              workflow_id: workflowId,
              conversation_id: conversationId,
              answer: text,
            }),
          },
        );

        const data: ReplyResponse = await response.json();

        setExtracted(data.extracted ?? {});
        setPriority(data.priority ?? null);
        setMissingFields(data.missing_fields ?? []);
        setCompleted(data.completed);

        if (data.question) {
          appendMessage("agent", data.question);
        }
      }
    } catch {
      appendMessage(
        "agent",
        "Sorry, something went wrong reaching the server. Please try again.",
      );
    } finally {
      setIsSending(false);
    }
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Enter") {
      handleSend();
    }
  }

  const collectedCount = started
    ? FIELDS.filter((field) => !missingFields.includes(field.key)).length
    : 0;

  const progressPct = Math.round((collectedCount / FIELDS.length) * 100);

  const statusText = completed
    ? "Completed"
    : started
      ? "In Progress"
      : "Not Started";

  const statusClass = completed ? "completed" : started ? "progress" : "idle";
  const priorityKey = (priority ?? "unknown").toLowerCase();

  return (
    <div className="page">
      <div className="aurora aurora-a" />
      <div className="aurora aurora-b" />
      <div className="aurora aurora-c" />

      <div className="app-shell">
        <aside className="sidebar">
          <div className="sidebar-topbar">
            <div className="brand">
              <div className="brand-icon">
                <Sparkles size={18} strokeWidth={2.25} />
              </div>
              <div>
                <h1>MedFlow</h1>
                <span className="brand-subtitle">AI Patient Intake</span>
              </div>
            </div>
          </div>

          <div className="status-panel">
            <div className="status-card">
              <span className="status-label">Intake Status</span>
              <span className={`status-pill ${statusClass}`}>
                <span className="status-dot" />
                {statusText}
              </span>
            </div>

            <div className="status-card">
              <span className="status-label">Priority</span>
              <span className={`priority-pill priority-${priorityKey}`}>
                <span className="priority-dot" />
                {priority ?? "—"}
              </span>
            </div>

            <div className="status-section">
              <div className="status-section-header">
                <h3>Patient Information</h3>
                {started && (
                  <span className="progress-text">
                    {collectedCount}/{FIELDS.length}
                  </span>
                )}
              </div>

              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${started ? progressPct : 0}%` }}
                />
              </div>

              <ul className="field-checklist">
                {FIELDS.map((field) => {
                  const isDone =
                    started && !missingFields.includes(field.key);
                  const value = extracted[field.key];
                  const Icon = field.icon;

                  return (
                    <li
                      key={field.key}
                      className={isDone ? "field-done" : "field-pending"}
                    >
                      <span className="field-status-icon">
                        {isDone ? (
                          <CheckCircle2 size={16} strokeWidth={2.4} />
                        ) : (
                          <Icon size={15} strokeWidth={2} />
                        )}
                      </span>

                      <div className="field-text">
                        <span className="field-label">{field.label}</span>

                        {isDone && value && (
                          <span className="field-value">{value}</span>
                        )}
                      </div>
                    </li>
                  );
                })}
              </ul>
            </div>
          </div>

          <div className="privacy">
            <Lock size={14} strokeWidth={2.2} />
            <p>Your information is secure and private.</p>
          </div>
        </aside>

        <main className="chat-area">
          <header className="chat-header">
            <div className="agent-avatar">
              <Bot size={20} strokeWidth={2} />
            </div>

            <div className="chat-header-info">
              <h2>MedFlow AI Assistant</h2>
              <p>
                {completed
                  ? "intake complete"
                  : isSending
                    ? "typing…"
                    : "online"}
              </p>
            </div>
          </header>

          <div className="messages" ref={messagesContainerRef}>
            {messages.map((message) => (
              <div key={message.id} className={`message-row ${message.role}`}>
                {message.role === "agent" && (
                  <div className="message-avatar">
                    <Bot size={15} strokeWidth={2} />
                  </div>
                )}

                <div className="message-content">
                  <div className="message-bubble">
                    <span className="message-text">{message.text}</span>

                    <span className="message-meta">
                      {message.time}

                      {message.role === "user" && (
                        <CheckCircle2
                          className="checkmarks"
                          size={13}
                          strokeWidth={2.4}
                        />
                      )}
                    </span>
                  </div>
                </div>
              </div>
            ))}

            {isSending && (
              <div className="message-row agent">
                <div className="message-avatar">
                  <Bot size={15} strokeWidth={2} />
                </div>

                <div className="message-content">
                  <div className="message-bubble typing-bubble">
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                  </div>
                </div>
              </div>
            )}
          </div>

          {!completed ? (
            <div className="composer">
              <span className="composer-icon">
                <Smile size={20} strokeWidth={1.8} />
              </span>

              <input
                type="text"
                value={input}
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={
                  started ? "Type your answer…" : "Describe the referral…"
                }
                disabled={isSending}
              />

              <button
                type="button"
                className="send-button"
                onClick={handleSend}
                aria-label="Send"
                disabled={isSending || !input.trim()}
              >
                <Send size={17} strokeWidth={2.2} />
              </button>
            </div>
          ) : (
            <div className="completed-message">
              <CheckCircle2 size={16} strokeWidth={2.4} />
              Intake is complete. Thank you!
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
