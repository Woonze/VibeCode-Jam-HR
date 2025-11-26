import React, { useRef, useState, useEffect } from "react";
import Editor from "@monaco-editor/react";
import "./Workspace.css";

const logoUrl = "../content/FoturLogoSquare.png";

// === Типы ===
type ChatMessage = {
  id: string;
  role: "assistant" | "user";
  content: string;
  buttons?: { id: string; label: string; value: string }[];
};

type Task = {
  id: string;
  title: string;
  description: string;
  language: "javascript" | "python";
  template: string;
};

export default function Workspace() {
  const editorRef = useRef<any>(null);
  const chatRef = useRef<HTMLDivElement | null>(null);

  const [track, setTrack] = useState<null | "js" | "python">(null);
  const [task, setTask] = useState<Task | null>(null);

  const [value, setValue] = useState<string>("");
  const [log, setLog] = useState<string[]>([]);
  const [feedback, setFeedback] = useState<any>(null);
  const [running, setRunning] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [interviewFinished, setInterviewFinished] = useState(false);

  const [waitingCommunication, setWaitingCommunication] = useState(false);
  const [communicationQuestion, setCommunicationQuestion] = useState("");
  const [communicationAnswer, setCommunicationAnswer] = useState("");

  const [serverMsgCount, setServerMsgCount] = useState(0);


  // === начальные сообщения ===
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome-1",
      role: "assistant",
      content: "Привет! Перед началом выбери направление собеседования.",
    },
    {
      id: "welcome-2",
      role: "assistant",
      content: "На каком языке хочешь проходить интервью?",
      buttons: [
        { id: "js-btn", label: "JavaScript", value: "js" },
        { id: "py-btn", label: "Python", value: "python" },
      ],
    },
  ]);

  // автоскролл чата
  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTo({
        top: chatRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages, isTyping]);

  useEffect(() => {
    if (task) setValue(task.template);
  }, [task]);

  // ================================
  //   Выбор языка
  // ================================
  async function onSelectTrack(language: "js" | "python") {
    setTrack(language);

    setMessages(prev =>
      prev.map(m => ({ ...m, buttons: undefined }))
    );

    setMessages(prev => [
      ...prev,
      {
        id: `user-${Date.now()}`,
        role: "user",
        content: `Выбираю направление: ${language.toUpperCase()}`
      }
    ]);

    await fetch("/api/select_track", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ track: language }),
    });

    // Запускаем интервью ПОСЛЕ выбора
    await startInterview();
  }


  // ================================
  //   Старт интервью
  // ================================
  async function startInterview() {
    setIsTyping(true);

    const res = await fetch("/api/start_interview", {
      method: "POST",
    });

    const data = await res.json();
    setIsTyping(false);

    if (Array.isArray(data.messages)) {
      setMessages(prev => {
        const newServer = data.messages.slice(serverMsgCount);
        return [...prev, ...newServer];
      });
      setServerMsgCount(data.messages.length);
    }

    if (data.task) {
      setTask(data.task);
      setValue(data.task.template);
    }
  }

  // ================================
  //   Запуск кода
  // ================================
  async function onRunCode() {
    if (!task) return;
    if (running) return;

    setRunning(true);
    setLog((l) => [...l, "Отправка кода в песочницу..."]);

    const res = await fetch("/api/compile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        code: value,
        language: task.language,
        taskId: task.id,
      }),
    });

    const data = await res.json();
    setLog((l) => [...l, data.stdout || data.error || "нет вывода"]);

    setRunning(false);
  }

  // ================================
  //   Отправка решения
  // ================================
  async function onDoneButton() {
    if (!task) return;

    // Если сейчас нужно отвечать на вопрос
    if (waitingCommunication) {
      await sendCommunicationAnswer();
      return;
    }
    
    setIsTyping(true);

    const res = await fetch("/api/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        taskId: task.id,
        code: value,
      }),
    });

    const data = await res.json();
    setIsTyping(false);

    setFeedback(data);

    if (Array.isArray(data.messages)) {
      setMessages(prev => {
        const newServer = data.messages.slice(serverMsgCount);
        return [...prev, ...newServer];
      });
      setServerMsgCount(data.messages.length);
    }


    // если бэкенд ожидает ответ на вопрос
    if (data.ask_communication) {
      setWaitingCommunication(true);
      setCommunicationQuestion(data.communication_question);
      return;
    }

    if (data.task) {
      setTask(data.task);
      setValue(data.task.template);
    }

    if (data.finished) {
      setInterviewFinished(true);
    }
  }

  async function sendCommunicationAnswer() {
  setMessages(prev => [
    ...prev,
    {
      id: `user-${Date.now()}`,
      role: "user",
      content: communicationAnswer
    }
  ]);

  setIsTyping(true);

  const res = await fetch("/api/communication_answer", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      answer: communicationAnswer
    }),
  });

  const data = await res.json();
  setIsTyping(false);

  if (Array.isArray(data.messages)) {
    setMessages(prev => {
      const newServer = data.messages.slice(serverMsgCount);
      return [...prev, ...newServer];
    });
    setServerMsgCount(data.messages.length);
  }


  if (data.task) {
    setTask(data.task);
    setValue(data.task.template);
  }

  if (data.finished) {
    setInterviewFinished(true);
  }

  // выходим из режима общения
  setWaitingCommunication(false);
  setCommunicationAnswer("");
  setCommunicationQuestion("");
}


  // ================================
  //   Рендер
  // ================================
  return (
    <div className="ws-root">
      <div className="ws-shell">
        {/* HEADER */}
        <header className="ws-topbar">
          <div className="ws-topbar-left">
            <img src={logoUrl} className="ws-logo" />

            <div className="ws-app-info">
              <div className="ws-app-title">AI HR Assessment</div>

              <div className="ws-app-subtitle">
                Live coding interview
                {track ? ` • ${track.toUpperCase()}` : ""}
              </div>
            </div>
          </div>

          <div className="ws-topbar-right">
            <div className="ws-candidate-label">
              Кандидат: <span>Фотур Фотуров</span>
            </div>

            {task && (
              <div className="ws-task-label">
                Текущее задание: <span>{task.id}</span>
              </div>
            )}
          </div>
        </header>

        {/* MAIN */}
        <div className="ws-main">

          {/* LEFT: чат */}
          <section className="ws-left">
            {/* Task Card */}
            {task && (
              <div className="ws-task-card">
                <div className="ws-task-header">
                  <span className="ws-task-pill">Текущее задание</span>
                  <span className="ws-task-id">{task.id}</span>
                </div>

                <div className="ws-task-title">{task.title}</div>
                <p className="ws-task-desc">{task.description}</p>
              </div>
            )}

            {/* Chat */}
            <div className="ws-chat-panel">
              <div className="ws-chat-body" ref={chatRef}>
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={
                      msg.role === "assistant"
                        ? "ws-chat-row ws-chat-row-assistant"
                        : "ws-chat-row ws-chat-row-user"
                    }
                  >
                    {msg.role === "assistant" && (
                      <div className="ws-avatar ws-avatar-ai">AI</div>
                    )}

                    <div
                      className={
                        msg.role === "assistant"
                          ? "ws-bubble ws-bubble-ai"
                          : "ws-bubble ws-bubble-user"
                      }
                    >
                      <pre className="ws-bubble-text">{msg.content}</pre>

                      {/* inline buttons (JS / Python) */}
                      {msg.buttons && (
                        <div className="ws-button-row">
                          {msg.buttons.map((btn) => (
                            <button
                              key={btn.id}
                              className="ws-inline-btn"
                              onClick={() =>
                                onSelectTrack(btn.value as any)
                              }
                            >
                              {btn.label}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>

                    {msg.role === "user" && (
                      <div className="ws-avatar ws-avatar-user">Я</div>
                    )}
                  </div>
                ))}

                {isTyping && (
                  <div className="ws-chat-row ws-chat-row-assistant">
                    <div className="ws-avatar ws-avatar-ai">AI</div>
                    <div className="ws-bubble ws-bubble-ai ws-typing-bubble">
                      <span className="ws-typing-dot" />
                      <span className="ws-typing-dot ws-typing-dot-delay1" />
                      <span className="ws-typing-dot ws-typing-dot-delay2" />
                    </div>
                  </div>
                )}
              </div>

              {/* Chat Footer */}
              {track && task && (
                <div className="ws-chat-footer">

                  {interviewFinished ? (
                    <div className="ws-finished-banner">
                      Интервью завершено 🎉  
                    </div>
                  ) : waitingCommunication ? (
                    <>
                      <textarea
                        className="ws-comm-input"
                        placeholder="Введите ответ..."
                        value={communicationAnswer}
                        onChange={(e) => setCommunicationAnswer(e.target.value)}
                        style={{
                          width: "100%",
                          height: "80px",
                          resize: "none",
                          marginBottom: 10,
                        }}
                      />
                      <button
                        className="ws-btn ws-btn-primary"
                        onClick={sendCommunicationAnswer}
                      >
                        Ответить
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        className="ws-btn ws-btn-secondary"
                        onClick={onRunCode}
                      >
                        Запустить в песочнице
                      </button>

                      <button
                        className="ws-btn ws-btn-primary"
                        onClick={onDoneButton}
                      >
                        Готово - отправить
                      </button>
                    </>
                  )}
                </div>
              )}
            </div>
          </section>

          {/* RIGHT: Editor + logs */}
          <section className="ws-right">
            {track && task && (
              <>
                <div className="ws-editor-panel">
                  <div className="ws-editor-header">
                    <div className="ws-editor-title">
                      Редактор решения
                      <span className="ws-editor-lang-tag">
                        {(task.language || "javascript").toUpperCase()}
                      </span>
                    </div>
                  </div>

                  <div className="ws-editor-body">
                    <Editor
                      height="100%"
                      defaultLanguage={task?.language || "javascript"}
                      value={value}
                      onChange={(v) => setValue(v || "")}
                      theme="vs-dark"
                    />
                  </div>
                </div>

                <div className="ws-bottom-panels">
                  <div className="ws-panel ws-log-panel">
                    <div className="ws-panel-header">Логи</div>
                    <div className="ws-panel-body ws-log-body">
                      {log.map((l, i) => (
                        <div key={i} className="ws-log-line">
                          {l}
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="ws-panel ws-feedback-panel">
                    <div className="ws-panel-header">Фидбек</div>
                    <div className="ws-panel-body">
                      {feedback ? (
                        <div className="ws-feedback-content">
                          {feedback.score !== undefined && (
                            <div className="ws-feedback-score">
                              Оценка: <span>{feedback.score}/100</span>
                            </div>
                          )}

                          {feedback.comment && (
                            <div className="ws-feedback-comment">
                              <div className="ws-feedback-label">Комментарий ИИ:</div>
                                <p>{feedback.comment}</p>
                              </div>
                          )}

                          {feedback.report && (
                            <div className="ws-feedback-report">
                              <a href={feedback.report} target="_blank">Открыть PDF отчёт</a>
                            </div>
                          )}
                        </div>
                      ) : (
                        "Фидбек появится после отправки решения."
                      )}
                    </div>
                  </div>
                </div>
              </>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
