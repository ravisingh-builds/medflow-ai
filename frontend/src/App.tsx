import { useState } from "react";
import "./App.css";

type Message = {
  id: number;
  role: "agent" | "user";
  text: string;
  time: string;
};

type ChatSession = {
  id: string;
  workflowId: string;
  conversationId: string;
  title: string;
  messages: Message[];
  completed: boolean;
  lastMessage: string;
  lastTime: string;
};

type LeadResponse = {
  lead_id: string;
  conversation_id: string;
  question: string;
  workflow_id: string;
};

type ReplyResponse = {
  workflow_id: string;
  question: string | null;
  completed: boolean;
};

function getTime() {
  return new Date().toLocaleTimeString([], {
    hour: "numeric",
    minute: "2-digit",
  });
}

function makeTitle(referral: string) {
  const trimmed = referral.trim().replace(/\s+/g, " ");

  if (trimmed.length <= 34) {
    return trimmed || "New Patient Referral";
  }

  return `${trimmed.slice(0, 34)}…`;
}

function App() {
  const [chats, setChats] = useState<ChatSession[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [composingNew, setComposingNew] = useState(false);
  const [search, setSearch] = useState("");

  const [referral, setReferral] = useState("");
  const [answer, setAnswer] = useState("");

  const activeChat = chats.find((chat) => chat.id === activeChatId) ?? null;

  const filteredChats = chats.filter((chat) => {
    const query = search.trim().toLowerCase();

    if (!query) {
      return true;
    }

    return (
      chat.title.toLowerCase().includes(query) ||
      chat.lastMessage.toLowerCase().includes(query)
    );
  });

  function bumpChat(id: string, updater: (chat: ChatSession) => ChatSession) {
    setChats((previous) => {
      const index = previous.findIndex((chat) => chat.id === id);

      if (index === -1) {
        return previous;
      }

      const updated = updater(previous[index]);
      const rest = previous.filter((_, i) => i !== index);

      return [updated, ...rest];
    });
  }

  function openNewChat() {
    setComposingNew(true);
    setActiveChatId(null);
  }

  async function startIntake() {
    if (!referral.trim()) {
      return;
    }

    const submittedReferral = referral.trim();

    const response = await fetch("http://localhost:8000/leads", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        referral: submittedReferral,
      }),
    });

    const data: LeadResponse = await response.json();
    const time = getTime();

    const newChat: ChatSession = {
      id: data.workflow_id,
      workflowId: data.workflow_id,
      conversationId: data.conversation_id,
      title: makeTitle(submittedReferral),
      messages: [
        {
          id: Date.now(),
          role: "agent",
          text: data.question,
          time,
        },
      ],
      completed: false,
      lastMessage: data.question,
      lastTime: time,
    };

    setChats((previous) => [newChat, ...previous]);
    setActiveChatId(newChat.id);
    setComposingNew(false);
    setReferral("");
  }

  async function sendAnswer() {
    if (!activeChat || !answer.trim()) {
      return;
    }

    const currentAnswer = answer.trim();
    const chatId = activeChat.id;

    setAnswer("");

    bumpChat(chatId, (chat) => ({
      ...chat,
      messages: [
        ...chat.messages,
        {
          id: Date.now(),
          role: "user",
          text: currentAnswer,
          time: getTime(),
        },
      ],
      lastMessage: currentAnswer,
      lastTime: getTime(),
    }));

    const response = await fetch(
      "http://localhost:8000/conversation/reply",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          workflow_id: activeChat.workflowId,
          conversation_id: activeChat.conversationId,
          answer: currentAnswer,
        }),
      },
    );

    const data: ReplyResponse = await response.json();

    bumpChat(chatId, (chat) => {
      if (!data.question) {
        return { ...chat, completed: data.completed };
      }

      const time = getTime();

      return {
        ...chat,
        completed: data.completed,
        messages: [
          ...chat.messages,
          {
            id: Date.now() + 1,
            role: "agent",
            text: data.question,
            time,
          },
        ],
        lastMessage: data.question,
        lastTime: time,
      };
    });
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Enter") {
      sendAnswer();
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-topbar">
          <div className="brand">
            <div className="brand-icon">✚</div>
            <h1>MedFlow</h1>
          </div>

          <div className="sidebar-topbar-icons">
            <span
              title="New intake"
              onClick={openNewChat}
              className="new-chat-icon"
            >
              ✏️
            </span>
            <span title="Menu">⋮</span>
          </div>
        </div>

        <div className="search-bar">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search chats"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>

        <div className="chat-list">
          {filteredChats.length === 0 && (
            <div className="chat-list-empty">
              <p>No conversations yet</p>
              <button type="button" onClick={openNewChat}>
                + Start new intake
              </button>
            </div>
          )}

          {filteredChats.map((chat) => (
            <div
              key={chat.id}
              className={`chat-list-item ${
                chat.id === activeChatId ? "active" : ""
              }`}
              onClick={() => {
                setActiveChatId(chat.id);
                setComposingNew(false);
              }}
            >
              <div className="chat-list-avatar">🧑</div>

              <div className="chat-list-info">
                <div className="chat-list-row">
                  <span className="chat-list-title">{chat.title}</span>
                  <span className="chat-list-time">{chat.lastTime}</span>
                </div>

                <div className="chat-list-row">
                  <span className="chat-list-preview">
                    {chat.lastMessage}
                  </span>

                  {chat.completed && (
                    <span className="chat-list-badge">✓ Done</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </aside>

      <main className="chat-area">
        {!activeChat && !composingNew && (
          <div className="chat-placeholder">
            <div className="chat-placeholder-icon">✚</div>
            <h2>MedFlow AI</h2>
            <p>
              Select a conversation from the left, or start a new patient
              intake to begin collecting referral information.
            </p>
            <button type="button" onClick={openNewChat}>
              + Start new intake
            </button>
          </div>
        )}

        {composingNew && (
          <>
            <header className="chat-header">
              <div className="agent-avatar">🤖</div>

              <div className="chat-header-info">
                <h2>New Patient Intake</h2>
                <p>Enter the referral details to begin</p>
              </div>
            </header>

            <div className="welcome">
              <h2>New Referral</h2>

              <p>
                Paste or type the referral information below. Our AI
                assistant will extract the key details and ask follow-up
                questions for anything missing.
              </p>

              <textarea
                value={referral}
                onChange={(event) => setReferral(event.target.value)}
                placeholder="Tell us what's going on..."
                rows={5}
              />

              <button
                className="start-button"
                type="button"
                onClick={startIntake}
              >
                Start Intake
              </button>
            </div>
          </>
        )}

        {activeChat && (
          <>
            <header className="chat-header">
              <div className="agent-avatar">🤖</div>

              <div className="chat-header-info">
                <h2>{activeChat.title}</h2>
                <p>{!activeChat.completed ? "online" : "intake complete"}</p>
              </div>

              <div className="chat-header-icons">
                <span title="Search">🔍</span>
                <span title="Menu">⋮</span>
              </div>
            </header>

            <div className="messages">
              {activeChat.messages.map((message) => (
                <div
                  key={message.id}
                  className={`message-row ${message.role}`}
                >
                  {message.role === "agent" && (
                    <div className="message-avatar">🤖</div>
                  )}

                  <div className="message-content">
                    <div className="message-bubble">
                      <span className="message-text">{message.text}</span>

                      <span className="message-meta">
                        {message.time}

                        {message.role === "user" && (
                          <span className="checkmarks">✓✓</span>
                        )}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {!activeChat.completed && (
              <div className="composer">
                <span className="composer-icon">😊</span>

                <input
                  type="text"
                  value={answer}
                  onChange={(event) => setAnswer(event.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Type a message"
                />

                <button
                  type="button"
                  className="send-button"
                  onClick={sendAnswer}
                  aria-label="Send"
                >
                  ➤
                </button>
              </div>
            )}

            {activeChat.completed && (
              <div className="completed-message">
                ✓ Intake is complete for this patient.
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;
