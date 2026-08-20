import { useCallback, useEffect, useRef, useState } from "react";
import {
  Activity,
  Banknote,
  Bot,
  CalendarDays,
  CheckCircle2,
  Clock,
  Lock,
  Pencil,
  Plus,
  RotateCcw,
  Send,
  Smile,
  Sparkles,
  Stethoscope,
  User,
  UserRound,
  X,
  type LucideIcon,
} from "lucide-react";
import "./App.css";

const API_BASE = "http://localhost:8000";

type Message = {
  id: number;
  role: "agent" | "user";
  text: string;
  time: string;
};

type ExtractedFields = Record<string, string | null | undefined>;

type AppointmentSlot = {
  id: string;
  label: string;
  starts_at: string;
  ends_at: string;
  doctor_name: string;
};

type Appointment = {
  id: string;
  lead_id: string;
  conversation_id: string | null;
  workflow_id: string;
  slot_id: string;
  starts_at: string;
  ends_at: string;
  doctor_name: string;
  priority: string;
  status: string;
  label: string;
};

type LeadResponse = {
  lead_id: string;
  conversation_id: string;
  question: string | null;
  field: string | null;
  workflow_id: string;
  extracted: ExtractedFields;
  priority: string;
  missing_fields: string[];
  completed: boolean;
  awaiting_slots: boolean;
  offered_slots: AppointmentSlot[];
  appointment: Appointment | null;
  booking_message: string | null;
};

type ReplyResponse = {
  workflow_id: string;
  question: string | null;
  field: string | null;
  completed: boolean;
  awaiting_slots: boolean;
  offered_slots: AppointmentSlot[];
  appointment: Appointment | null;
  booking_message: string | null;
  extracted: ExtractedFields;
  priority: string;
  missing_fields: string[];
};

type ResumableConversation = {
  conversation_id: string;
  workflow_id: string;
  lead_id: string;
  patient_name: string;
  chief_complaint: string | null;
  priority: string;
  current_question: string;
  created_at: string;
  updated_at: string;
};

type ResumeResponse = {
  workflow_id: string;
  conversation_id: string | null;
  lead_id: string | null;
  patient_name: string | null;
  chief_complaint: string | null;
  question: string | null;
  field: string | null;
  extracted: ExtractedFields;
  priority: string;
  missing_fields: string[];
  completed: boolean;
  awaiting_slots: boolean;
  offered_slots: AppointmentSlot[];
  appointment: Appointment | null;
  booking_message: string | null;
};

type CorrectionResponse = {
  workflow_id: string;
  field: string | null;
  old_value?: string | null;
  applied: boolean;
  message: string;
  extracted: ExtractedFields;
};

type ReviewMessage = {
  id: number;
  role: "agent" | "user";
  text: string;
  time: string;
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

function timeAgo(iso: string): string {
  const diffMs = Math.max(0, Date.now() - new Date(iso).getTime());
  const minutes = Math.round(diffMs / 60000);

  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes}m ago`;

  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours}h ago`;

  const days = Math.round(hours / 24);
  return `${days}d ago`;
}

function formatAppointmentWhen(iso: string): string {
  const date = new Date(iso);
  return date.toLocaleString([], {
    weekday: "short",
    month: "short",
    day: "numeric",
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
  const [awaitingSlots, setAwaitingSlots] = useState(false);
  const [offeredSlots, setOfferedSlots] = useState<AppointmentSlot[]>([]);
  const [appointment, setAppointment] = useState<Appointment | null>(null);
  const [scheduledAppointments, setScheduledAppointments] = useState<
    Appointment[]
  >([]);

  const [workflowId, setWorkflowId] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);

  const [extracted, setExtracted] = useState<ExtractedFields>({});
  const [priority, setPriority] = useState<string | null>(null);
  const [missingFields, setMissingFields] = useState<string[]>([]);

  const [resumable, setResumable] = useState<ResumableConversation[]>([]);
  const [isResuming, setIsResuming] = useState(false);

  const [reviewingAppointment, setReviewingAppointment] =
    useState<Appointment | null>(null);
  const [reviewExtracted, setReviewExtracted] = useState<ExtractedFields>({});
  const [reviewMessages, setReviewMessages] = useState<ReviewMessage[]>([]);
  const [isLoadingReview, setIsLoadingReview] = useState(false);
  const [isSendingCorrection, setIsSendingCorrection] = useState(false);

  const messagesContainerRef = useRef<HTMLDivElement>(null);

  const refreshResumable = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/conversation/resumable`);

      if (!response.ok) {
        return;
      }

      const data: ResumableConversation[] = await response.json();
      setResumable(data);
    } catch {
      // Sidebar list is a nice-to-have — a failed refresh shouldn't
      // interrupt whatever the user is doing in the chat itself.
    }
  }, []);

  const refreshAppointments = useCallback(async () => {
    try {
      const response = await fetch(
        `${API_BASE}/appointments?status=SCHEDULED`,
      );
      if (!response.ok) {
        return;
      }
      const data: Appointment[] = await response.json();
      setScheduledAppointments(data);
    } catch {
      // Same as resumable — non-blocking for the chat.
    }
  }, []);

  useEffect(() => {
    refreshResumable();
    refreshAppointments();
  }, [refreshResumable, refreshAppointments]);

  useEffect(() => {
    const container = messagesContainerRef.current;

    if (!container) {
      return;
    }

    container.scrollTo({
      top: container.scrollHeight,
      behavior: "smooth",
    });
  }, [messages.length, isSending, awaitingSlots, offeredSlots.length]);

  function appendMessage(role: Message["role"], text: string) {
    setMessages((previous) => [
      ...previous,
      { id: nextId(), role, text, time: getTime() },
    ]);
  }

  function applyWorkflowPayload(
    data: Pick<
      ReplyResponse,
      | "extracted"
      | "priority"
      | "missing_fields"
      | "completed"
      | "awaiting_slots"
      | "offered_slots"
      | "appointment"
      | "booking_message"
      | "question"
    >,
    { appendQuestion = true }: { appendQuestion?: boolean } = {},
  ) {
    setExtracted(data.extracted ?? {});
    setPriority(data.priority ?? null);
    setMissingFields(data.missing_fields ?? []);
    setCompleted(Boolean(data.completed));
    setAwaitingSlots(Boolean(data.awaiting_slots));
    setOfferedSlots(data.offered_slots ?? []);

    if (data.appointment) {
      setAppointment(data.appointment);
    }

    if (appendQuestion && data.question) {
      appendMessage("agent", data.question);
    }

    if (data.completed && data.booking_message) {
      appendMessage("agent", data.booking_message);
    } else if (data.completed && data.appointment) {
      appendMessage(
        "agent",
        `You're booked for ${data.appointment.label}. We'll see you then!`,
      );
    }
  }

  async function sendReply(answer: string, displayText?: string): Promise<boolean> {
    if (!workflowId || !conversationId) {
      return false;
    }

    appendMessage("user", displayText ?? answer);
    setIsSending(true);

    try {
      const response = await fetch(`${API_BASE}/conversation/reply`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          workflow_id: workflowId,
          conversation_id: conversationId,
          answer,
        }),
      });

      const data: ReplyResponse = await response.json();
      applyWorkflowPayload(data);
      refreshResumable();
      refreshAppointments();
      return true;
    } catch {
      appendMessage(
        "agent",
        "Sorry, something went wrong reaching the server. Please try again.",
      );
      return false;
    } finally {
      setIsSending(false);
    }
  }

  async function handleSend() {
    const text = input.trim();

    if (!text) {
      return;
    }

    if (reviewingAppointment) {
      if (isSendingCorrection || isLoadingReview) {
        return;
      }
      setInput("");
      await handleSendCorrection(text);
      return;
    }

    if (isSending || isResuming || completed || awaitingSlots) {
      return;
    }

    setInput("");
    appendMessage("user", text);
    setIsSending(true);

    try {
      if (!started) {
        const response = await fetch(`${API_BASE}/leads`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ referral: text }),
        });

        const data: LeadResponse = await response.json();

        setWorkflowId(data.workflow_id);
        setConversationId(data.conversation_id);
        setStarted(true);
        applyWorkflowPayload(data);
        refreshResumable();
        refreshAppointments();
      } else {
        if (!workflowId || !conversationId) {
          return;
        }

        const response = await fetch(`${API_BASE}/conversation/reply`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            workflow_id: workflowId,
            conversation_id: conversationId,
            answer: text,
          }),
        });

        const data: ReplyResponse = await response.json();
        applyWorkflowPayload(data);
        refreshResumable();
        refreshAppointments();
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

  async function handleSlotSelect(slot: AppointmentSlot) {
    if (isSending || isResuming || !awaitingSlots) {
      return;
    }

    const previousSlots = offeredSlots;
    setAwaitingSlots(false);
    setOfferedSlots([]);

    const ok = await sendReply(slot.id, slot.label);
    if (!ok) {
      setAwaitingSlots(true);
      setOfferedSlots(previousSlots);
    }
  }

  async function handleCompleteAppointment(appointmentId: string) {
    try {
      const response = await fetch(
        `${API_BASE}/appointments/${appointmentId}/complete`,
        { method: "POST" },
      );
      if (!response.ok) {
        return;
      }
      if (appointment?.id === appointmentId) {
        setAppointment(null);
      }
      refreshAppointments();
    } catch {
      // Non-blocking
    }
  }

  async function handleSelectAppointment(item: Appointment) {
    if (reviewingAppointment?.id === item.id) {
      return;
    }

    setReviewingAppointment(item);
    setReviewExtracted({});
    setReviewMessages([]);
    setIsLoadingReview(true);

    try {
      const response = await fetch(
        `${API_BASE}/conversation/${item.workflow_id}/resume`,
      );

      if (!response.ok) {
        throw new Error("Unable to load appointment details");
      }

      const data: ResumeResponse = await response.json();
      const extractedFields = data.extracted ?? {};
      setReviewExtracted(extractedFields);

      const patientName = data.patient_name ?? "this patient";
      const lines = FIELDS.map((field) => {
        const value = extractedFields[field.key];
        return `${field.label}: ${value ? value : "Not provided"}`;
      });

      setReviewMessages([
        {
          id: nextId(),
          role: "agent",
          text: `Here's what we have on file for ${patientName}'s appointment (${item.label}):\n\n${lines.join("\n")}`,
          time: getTime(),
        },
        {
          id: nextId(),
          role: "agent",
          text:
            "Let me know if anything needs correcting — for example, " +
            '"please correct my date of birth to 1990-01-01".',
          time: getTime(),
        },
      ]);
    } catch {
      setReviewMessages([
        {
          id: nextId(),
          role: "agent",
          text: "Sorry, I couldn't load this appointment's details. Please try again.",
          time: getTime(),
        },
      ]);
    } finally {
      setIsLoadingReview(false);
    }
  }

  function closeReview() {
    setReviewingAppointment(null);
    setReviewExtracted({});
    setReviewMessages([]);
  }

  async function handleSendCorrection(text: string) {
    if (!reviewingAppointment || isSendingCorrection || isLoadingReview) {
      return;
    }

    setReviewMessages((previous) => [
      ...previous,
      { id: nextId(), role: "user", text, time: getTime() },
    ]);
    setIsSendingCorrection(true);

    try {
      const response = await fetch(
        `${API_BASE}/conversation/${reviewingAppointment.workflow_id}/correct`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text }),
        },
      );

      const data: CorrectionResponse = await response.json();
      setReviewExtracted(data.extracted ?? {});
      setReviewMessages((previous) => [
        ...previous,
        { id: nextId(), role: "agent", text: data.message, time: getTime() },
      ]);
    } catch {
      setReviewMessages((previous) => [
        ...previous,
        {
          id: nextId(),
          role: "agent",
          text: "Sorry, something went wrong reaching the server. Please try again.",
          time: getTime(),
        },
      ]);
    } finally {
      setIsSendingCorrection(false);
    }
  }

  function startNewIntake() {
    setMessages([
      { id: nextId(), role: "agent", text: GREETING, time: getTime() },
    ]);
    setInput("");
    setStarted(false);
    setCompleted(false);
    setAwaitingSlots(false);
    setOfferedSlots([]);
    setAppointment(null);
    setWorkflowId(null);
    setConversationId(null);
    setExtracted({});
    setPriority(null);
    setMissingFields([]);
    refreshResumable();
    refreshAppointments();
  }

  async function handleResume(item: ResumableConversation) {
    if (isSending || isResuming) {
      return;
    }

    setIsResuming(true);

    try {
      const response = await fetch(
        `${API_BASE}/conversation/${item.workflow_id}/resume`,
      );

      if (!response.ok) {
        throw new Error("Unable to resume conversation");
      }

      const data: ResumeResponse = await response.json();

      setWorkflowId(data.workflow_id);
      setConversationId(data.conversation_id);
      setExtracted(data.extracted ?? {});
      setPriority(data.priority ?? null);
      setMissingFields(data.missing_fields ?? []);
      setStarted(true);
      setCompleted(Boolean(data.completed));
      setAwaitingSlots(Boolean(data.awaiting_slots));
      setOfferedSlots(data.offered_slots ?? []);
      setAppointment(data.appointment ?? null);
      setInput("");

      const patientName = data.patient_name ?? item.patient_name;
      const history: Message[] = [
        {
          id: nextId(),
          role: "agent",
          text: `Welcome back — resuming the intake for ${patientName}.`,
          time: getTime(),
        },
      ];

      FIELDS.forEach((field) => {
        const value = data.extracted?.[field.key];
        const isAnswered =
          Boolean(value) && !data.missing_fields.includes(field.key);

        if (isAnswered) {
          history.push({
            id: nextId(),
            role: "agent",
            text: `${field.label}?`,
            time: getTime(),
          });
          history.push({
            id: nextId(),
            role: "user",
            text: String(value),
            time: getTime(),
          });
        }
      });

      if (data.completed && data.appointment) {
        history.push({
          id: nextId(),
          role: "agent",
          text: `You're booked for ${data.appointment.label}. We'll see you then!`,
          time: getTime(),
        });
      } else if (data.awaiting_slots && data.question) {
        history.push({
          id: nextId(),
          role: "agent",
          text: data.question,
          time: getTime(),
        });
      } else if (data.completed) {
        history.push({
          id: nextId(),
          role: "agent",
          text: "This intake was already completed — nothing left to do here.",
          time: getTime(),
        });
      } else if (data.question) {
        history.push({
          id: nextId(),
          role: "agent",
          text: data.question,
          time: getTime(),
        });
      }

      setMessages(history);
      refreshResumable();
      refreshAppointments();
    } catch {
      appendMessage(
        "agent",
        "Couldn't resume that conversation. Please try again.",
      );
    } finally {
      setIsResuming(false);
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

  const visibleResumable = resumable.filter(
    (item) => item.workflow_id !== workflowId,
  );

  const sidebarAppointments = scheduledAppointments.filter(
    (item) => item.status === "SCHEDULED",
  );

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
            <div className="resume-section">
              <div className="resume-section-header">
                <h3>Paused Conversations</h3>

                {started && (
                  <button
                    type="button"
                    className="new-intake-button"
                    onClick={startNewIntake}
                    disabled={isResuming}
                  >
                    <Plus size={13} strokeWidth={2.4} />
                    New
                  </button>
                )}
              </div>

              {visibleResumable.length === 0 ? (
                <p className="resume-empty">
                  Nothing waiting to be resumed right now.
                </p>
              ) : (
                <ul className="resume-list">
                  {visibleResumable.map((item) => {
                    const itemPriorityKey = (
                      item.priority ?? "unknown"
                    ).toLowerCase();

                    return (
                      <li key={item.conversation_id}>
                        <button
                          type="button"
                          className="resume-item"
                          onClick={() => handleResume(item)}
                          disabled={isSending || isResuming}
                        >
                          <span className="resume-item-top">
                            <span className="resume-item-name">
                              {item.patient_name}
                            </span>
                            <span
                              className={`priority-pill priority-${itemPriorityKey} resume-priority`}
                            >
                              {item.priority}
                            </span>
                          </span>

                          <span className="resume-item-question">
                            {item.current_question}
                          </span>

                          <span className="resume-item-meta">
                            <Clock size={11} strokeWidth={2.2} />
                            Paused {timeAgo(item.updated_at)}
                            <RotateCcw
                              className="resume-icon"
                              size={12}
                              strokeWidth={2.2}
                            />
                            Resume
                          </span>
                        </button>
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>

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

            <div className="status-section appointment-section">
              <div className="status-section-header">
                <h3>Appointments</h3>
              </div>

              {sidebarAppointments.length === 0 ? (
                <p className="resume-empty">No upcoming appointments.</p>
              ) : (
                <ul className="appointment-list">
                  {sidebarAppointments.map((item) => (
                    <li
                      key={item.id}
                      className={`appointment-card${
                        reviewingAppointment?.id === item.id
                          ? " appointment-card-selected"
                          : ""
                      }`}
                    >
                      <button
                        type="button"
                        className="appointment-card-select"
                        onClick={() => handleSelectAppointment(item)}
                      >
                        <div className="appointment-card-top">
                          <CalendarDays size={15} strokeWidth={2.2} />
                          <span className="appointment-doctor">
                            {item.doctor_name}
                          </span>
                        </div>
                        <p className="appointment-when">
                          {formatAppointmentWhen(item.starts_at)}
                        </p>
                      </button>
                      <div className="appointment-card-meta">
                        <span
                          className={`priority-pill priority-${(
                            item.priority ?? "unknown"
                          ).toLowerCase()} resume-priority`}
                        >
                          {item.priority}
                        </span>
                        <button
                          type="button"
                          className="review-appointment-button"
                          onClick={() => handleSelectAppointment(item)}
                        >
                          <Pencil size={11} strokeWidth={2.4} />
                          Review
                        </button>
                        <button
                          type="button"
                          className="complete-appointment-button"
                          onClick={() => handleCompleteAppointment(item.id)}
                        >
                          Mark completed
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="status-section">
              <div className="status-section-header">
                <h3>
                  {reviewingAppointment
                    ? "Reviewing Patient Info"
                    : "Patient Information"}
                </h3>
                {reviewingAppointment ? (
                  <button
                    type="button"
                    className="new-intake-button"
                    onClick={closeReview}
                  >
                    <X size={12} strokeWidth={2.4} />
                    Close
                  </button>
                ) : (
                  started && (
                    <span className="progress-text">
                      {collectedCount}/{FIELDS.length}
                    </span>
                  )
                )}
              </div>

              {!reviewingAppointment && (
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${started ? progressPct : 0}%` }}
                  />
                </div>
              )}

              <ul className="field-checklist">
                {FIELDS.map((field) => {
                  const activeExtracted = reviewingAppointment
                    ? reviewExtracted
                    : extracted;
                  const value = activeExtracted[field.key];
                  const isDone = reviewingAppointment
                    ? Boolean(value)
                    : started && !missingFields.includes(field.key);
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
              <h2>
                {reviewingAppointment
                  ? "Reviewing Appointment"
                  : "MedFlow AI Assistant"}
              </h2>
              <p>
                {reviewingAppointment
                  ? isLoadingReview
                    ? "loading…"
                    : isSendingCorrection
                      ? "updating…"
                      : reviewingAppointment.label
                  : isResuming
                    ? "resuming…"
                    : awaitingSlots
                      ? "choose a time"
                      : completed
                        ? "intake complete"
                        : isSending
                          ? "typing…"
                          : "online"}
              </p>
            </div>

            {reviewingAppointment && (
              <button
                type="button"
                className="close-review-button"
                onClick={closeReview}
                aria-label="Close review"
              >
                <X size={18} strokeWidth={2.2} />
              </button>
            )}
          </header>

          <div className="messages" ref={messagesContainerRef}>
            {(reviewingAppointment ? reviewMessages : messages).map(
              (message) => (
                <div
                  key={message.id}
                  className={`message-row ${message.role}`}
                >
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
              ),
            )}

            {reviewingAppointment
              ? (isLoadingReview || isSendingCorrection) && (
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
                )
              : (isSending || isResuming) && (
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

          {reviewingAppointment ? (
            <div className="composer">
              <span className="composer-icon">
                <Pencil size={18} strokeWidth={1.8} />
              </span>

              <input
                type="text"
                value={input}
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={handleKeyDown}
                placeholder='e.g. "please correct my date of birth to 1990-01-01"'
                disabled={isSendingCorrection || isLoadingReview}
              />

              <button
                type="button"
                className="send-button"
                onClick={handleSend}
                aria-label="Send"
                disabled={
                  isSendingCorrection || isLoadingReview || !input.trim()
                }
              >
                <Send size={17} strokeWidth={2.2} />
              </button>
            </div>
          ) : awaitingSlots && !completed ? (
            <div className="slot-picker">
              <p className="slot-picker-hint">Select an available time</p>
              <div className="slot-options">
                {offeredSlots.map((slot) => (
                  <button
                    key={slot.id}
                    type="button"
                    className="slot-option"
                    onClick={() => handleSlotSelect(slot)}
                    disabled={isSending || isResuming}
                  >
                    <CalendarDays size={16} strokeWidth={2.2} />
                    <span>{slot.label}</span>
                  </button>
                ))}
              </div>
            </div>
          ) : !completed ? (
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
                disabled={isSending || isResuming}
              />

              <button
                type="button"
                className="send-button"
                onClick={handleSend}
                aria-label="Send"
                disabled={isSending || isResuming || !input.trim()}
              >
                <Send size={17} strokeWidth={2.2} />
              </button>
            </div>
          ) : (
            <div className="completed-message">
              <CheckCircle2 size={16} strokeWidth={2.4} />
              {appointment
                ? `Booked — ${appointment.label}`
                : "Intake is complete. Thank you!"}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
