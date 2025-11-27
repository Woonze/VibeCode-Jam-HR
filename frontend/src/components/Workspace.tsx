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

type TestResults = {
  name: string;
  passed: boolean;
  visible: boolean;
};


export default function Workspace() {
  const editorRef = useRef<any>(null);
  const chatRef = useRef<HTMLDivElement | null>(null);

  const [track, setTrack] = useState<null | "js" | "python">(null);
  const [task, setTask] = useState<Task | null>(null);
  const [softMode, setSoftMode] = useState(false);
  const [currentSoftTaskId, setCurrentSoftTaskId] = useState<string | null>(null);


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

  // === Античит: состояние ===
  const [antiCheatData, setAntiCheatData] = useState({
    pasteCount: 0,
    tabSwitchCount: 0,
    codeSnapshots: [] as Array<{ timestamp: number; code: string; length: number }>,
    lastAnalysisTime: Date.now(),
  });

  // === Античит: отслеживание вставок из буфера обмена ===
  // Используем ref для хранения предыдущей длины кода
  const prevCodeLengthRef = useRef<number>(0);
  const pasteTimeoutRef = useRef<number | null>(null);

  // Инициализируем длину при установке задачи
  useEffect(() => {
    if (task) {
      prevCodeLengthRef.current = value.length;
    }
  }, [task]);

  // Отслеживаем изменения в коде для определения вставок
  useEffect(() => {
    if (!task || prevCodeLengthRef.current === 0) {
      prevCodeLengthRef.current = value.length;
      return;
    }

    const currentLength = value.length;
    const prevLength = prevCodeLengthRef.current;
    const change = currentLength - prevLength;

    // Если код увеличился более чем на 15 символов за раз - вероятно вставка
    if (change > 15 && prevLength > 0) {
      // Очищаем предыдущий таймаут, если он есть
      if (pasteTimeoutRef.current) {
        clearTimeout(pasteTimeoutRef.current);
      }

      // Используем таймаут для группировки быстрых изменений
      pasteTimeoutRef.current = window.setTimeout(() => {
        const newPasteCount = antiCheatData.pasteCount + 1;
        console.log("[Античит] Обнаружена вставка из буфера обмена:", {
          taskId: task.id,
          pasteCount: newPasteCount,
          codeLengthChange: change,
          timestamp: new Date().toISOString(),
        });

        setAntiCheatData(prev => ({
          ...prev,
          pasteCount: newPasteCount,
        }));

        fetch("/api/anti_cheat_event", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            eventType: "paste",
            timestamp: Date.now(),
            taskId: task.id,
          }),
        })
          .then(() => {
            console.log("[Античит] Событие вставки отправлено на сервер");
          })
          .catch((error) => {
            console.error("[Античит] Ошибка при отправке события вставки:", error);
          });
      }, 100);
    }

    prevCodeLengthRef.current = currentLength;

    return () => {
      if (pasteTimeoutRef.current) {
        clearTimeout(pasteTimeoutRef.current);
      }
    };
  }, [value, task]);

  // === Античит: отслеживание выхода из вкладки ===
  useEffect(() => {
    if (!task) return;

    const handleVisibilityChange = () => {
      if (document.hidden) {
        const newTabSwitchCount = antiCheatData.tabSwitchCount + 1;
        console.log("[Античит] Обнаружен выход из вкладки (visibilitychange):", {
          taskId: task.id,
          tabSwitchCount: newTabSwitchCount,
          timestamp: new Date().toISOString(),
        });

        setAntiCheatData(prev => ({
          ...prev,
          tabSwitchCount: newTabSwitchCount,
        }));

        fetch("/api/anti_cheat_event", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            eventType: "tab_switch",
            timestamp: Date.now(),
            taskId: task.id,
          }),
        })
          .then(() => {
            console.log("[Античит] Событие выхода из вкладки отправлено на сервер");
          })
          .catch((error) => {
            console.error("[Античит] Ошибка при отправке события выхода из вкладки:", error);
          });
      }
    };

    const handleBlur = () => {
      const newTabSwitchCount = antiCheatData.tabSwitchCount + 1;
      console.log("[Античит] Обнаружен выход из окна (blur):", {
        taskId: task.id,
        tabSwitchCount: newTabSwitchCount,
        timestamp: new Date().toISOString(),
      });

      setAntiCheatData(prev => ({
        ...prev,
        tabSwitchCount: newTabSwitchCount,
      }));

      fetch("/api/anti_cheat_event", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          eventType: "window_blur",
          timestamp: Date.now(),
          taskId: task.id,
        }),
      })
        .then(() => {
          console.log("[Античит] Событие выхода из окна отправлено на сервер");
        })
        .catch((error) => {
          console.error("[Античит] Ошибка при отправке события выхода из окна:", error);
        });
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    window.addEventListener("blur", handleBlur);

    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      window.removeEventListener("blur", handleBlur);
    };
  }, [task]);

  // === Античит: периодический анализ кода каждые 20 секунд ===
  useEffect(() => {
    if (!task || interviewFinished) return;

    console.log("[Античит] Запущен периодический анализ кода (каждые 20 секунд) для задачи:", task.id);

    const interval = setInterval(() => {
      const currentCode = value;
      const timestamp = Date.now();
      const codeLength = currentCode.length;

      console.log("[Античит] Выполняется периодический анализ кода:", {
        taskId: task.id,
        codeLength,
        timestamp: new Date(timestamp).toISOString(),
        snapshotNumber: antiCheatData.codeSnapshots.length + 1,
      });

      // Сохраняем снимок кода
      setAntiCheatData(prev => ({
        ...prev,
        codeSnapshots: [
          ...prev.codeSnapshots,
          {
            timestamp,
            code: currentCode,
            length: codeLength,
          },
        ],
        lastAnalysisTime: timestamp,
      }));

      // Отправляем на анализ
      fetch("/api/anti_cheat_analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          taskId: task.id,
          code: currentCode,
          codeLength: codeLength,
          timestamp,
          taskDescription: task.description,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          console.log("[Античит] Результат анализа кода получен:", {
            taskId: task.id,
            cheatingProbability: data.analysis?.cheating_probability,
            riskLevel: data.analysis?.risk_level,
            suspiciousEventsCount: data.analysis?.suspicious_events?.length || 0,
          });
        })
        .catch((error) => {
          console.error("[Античит] Ошибка при отправке анализа кода:", error);
        });
    }, 20000); // 20 секунд

    return () => {
      console.log("[Античит] Периодический анализ кода остановлен для задачи:", task.id);
      clearInterval(interval);
    };
  }, [task, value, interviewFinished]);

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
      if (softMode) {
        await sendSoftAnswer();       // <-- новый путь
      } else {
        await sendCommunicationAnswer();
      }
      return;
    }
    
    setIsTyping(true);

    const res = await fetch("/api/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        taskId: task.id,
        code: value,
        runResult: feedback || null
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

    // === обработка soft-skills ===
    if (data.soft_question) {
      const soft = data.soft_question;

      setSoftMode(true);
      setCurrentSoftTaskId(soft.id);

      setTask({
          id: soft.id,
          title: "Soft-skills вопрос",
          description: soft.description,
          language: "javascript",
          template: soft.template
      });

      setValue(soft.template);

      // ВАЖНО !!!
      setWaitingCommunication(true);
      setCommunicationAnswer("");

      return;
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

  // === если пришёл soft-вопрос после 3-й задачи ===
  if (data.soft_question) {
    const soft = data.soft_question;

    setSoftMode(true);
    setCurrentSoftTaskId(soft.id);

    // переключаем текущую "задачу" на soft-вопрос
    setTask({
      id: soft.id,
      title: "Soft-skills вопрос",
      description: soft.description,
      language: "javascript", // просто заглушка
      template: soft.template,
    });

    setValue(soft.template);    // показываем шаблон справа
    setWaitingCommunication(true);  // показываем textarea
    setCommunicationAnswer("");     // чистим поле

    // здесь НЕ завершаем интервью
    return;
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

async function sendSoftAnswer() {
  if (!currentSoftTaskId) return;

  // показать ответ в чате
  setMessages(prev => [
    ...prev,
    {
      id: `user-${Date.now()}`,
      role: "user",
      content: communicationAnswer,
    },
  ]);

  setIsTyping(true);

  const res = await fetch("/api/soft_answer", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      taskId: currentSoftTaskId,
      answer: communicationAnswer,
    }),
  });

  const data = await res.json();
  setIsTyping(false);

  // подмешиваем сообщения сервера
  if (Array.isArray(data.messages)) {
    setMessages(prev => {
      const newServer = data.messages.slice(serverMsgCount);
      return [...prev, ...newServer];
    });
    setServerMsgCount(data.messages.length);
  }

  // если есть следующий soft-вопрос
  if (data.next_question) {
    const q = data.next_question;

    setTask({
      id: q.id,
      title: "Soft-skills вопрос",
      description: q.description,
      language: "javascript",
      template: q.template,
    });

    setValue(q.template);
    setCurrentSoftTaskId(q.id);
    setCommunicationAnswer("");
    setWaitingCommunication(true);
    return;
  }

  // если soft-интервью завершено
  if (data.finished) {
    setSoftMode(false);
    setWaitingCommunication(false);
    setInterviewFinished(true);
  }

  setCommunicationAnswer("");
}

  const getTaskDifficultyLabel = () => {
    if (!task) return "";

    // Для soft-части интерфейса
    if (softMode) return "soft-skill";

    const id = task.id.toLowerCase();

    if (id.includes("easy")) return "Легко";
    if (id.includes("med") || id.includes("medium")) return "Средне";
    if (id.includes("hard")) return "Сложно";

    // если ID какой-то особенный
    if (id.includes("soft")) return "soft-skill";

    return "Задание";
  };



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
                Текущее задание: <span>{getTaskDifficultyLabel()}</span>
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
                  <span className="ws-task-id">{getTaskDifficultyLabel()}</span>
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
                        onClick={onDoneButton}
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
                {/* ===== ВЕРХНЯЯ ПАНЕЛЬ: редактор ИЛИ soft-skills ===== */}
                {softMode ? (
                  // ---- Soft-skills режим: вместо редактора просто текст ----
                  <div className="ws-editor-panel ws-soft-panel">
                    <div className="ws-editor-header">
                      <div className="ws-editor-title">
                        Soft-skills интервью
                        <span className="ws-editor-lang-tag">Q&A</span>
                      </div>
                    </div>

                    <div className="ws-editor-body ws-soft-body">
                      <h3 className="ws-soft-question-title">{task.title}</h3>
                      <p className="ws-soft-question-desc">{task.description}</p>

                      {task.template && (
                        <>
                          <div className="ws-soft-hint-label">
                            Ситуация:
                          </div>
                          <pre className="ws-soft-template">
                            {task.template}
                          </pre>
                        </>
                      )}
                    </div>
                  </div>
                ) : (
                  // ---- Обычный режим: редактор кода ----
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
                        onMount={(editor) => {
                          editorRef.current = editor;
                        }}
                      />
                    </div>
                  </div>
                )}

                {/* ===== НИЖНЯЯ ПАНЕЛЬ: логи/тесты или заглушка для soft-skills ===== */}
                <div className="ws-bottom-panels">
                  {softMode ? (
                    <div className="ws-panel ws-soft-panel-info">
                      <div className="ws-panel-header">Soft-skills блок</div>
                      <div className="ws-panel-body">
                        Это часть интервью по soft-skills.<br />
                        Пишите ответ в поле слева внизу, кнопка
                        <b> «Ответить»</b> отправит его на оценку.<br />
                        Автотестов и логов здесь нет - оценка попадёт в итоговый отчёт.
                      </div>
                    </div>
                  ) : (
                    <>
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
                        <div className="ws-panel-header">Результаты тестов</div>
                        <div className="ws-panel-body">
                          {feedback && feedback.tests ? (
                            <div className="ws-tests-list">
                              {/* === ВИДИМЫЕ ТЕСТЫ === */}
                              {feedback.tests
                                .filter((t: TestResults) => t.visible)
                                .map((t: TestResults, i: number) => (
                                  <div key={i} className="ws-test-item">
                                    <span
                                      className={`ws-test-status ${
                                        t.passed ? "ok" : "fail"
                                      }`}
                                    >
                                      {t.passed ? "✔" : "✘"}
                                    </span>
                                    <span className="ws-test-name">{t.name}</span>
                                  </div>
                                ))}
                              {/* === СКРЫТЫЕ ТЕСТЫ (только итог статус) === */}
                              <div className="ws-hidden-tests-summary">
                                Скрытые тесты:{" "}
                                <b>
                                  {
                                    feedback.tests.filter(
                                      (t: TestResults) => !t.visible && t.passed
                                    ).length
                                  }
                                  /
                                  {
                                    feedback.tests.filter(
                                      (t: TestResults) => !t.visible
                                    ).length
                                  }
                                </b>
                              </div>
                            </div>
                          ) : (
                            <div>Тесты появятся после отправки решения.</div>
                          )}
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
