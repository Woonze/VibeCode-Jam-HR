import React, { useRef, useState, useEffect } from "react";
import Editor from "@monaco-editor/react";
import "./Workspace.css";

const logoUrl = "../content/FoturLogoSquare.png"; // путь к логотипу

type ChatMessage = {
  id: string;
  role: "assistant" | "user";
  content: string;
};

type Task = {
  id: string;
  title: string;
  description: string;
  language: "javascript";
  template: string;
};

type Feedback = {
  score?: number;
  comment?: string;
  report?: string;
  [key: string]: any;
};

export default function Workspace() {
  const editorRef = useRef<any>(null);
  const chatRef = useRef<HTMLDivElement | null>(null);

  const [task, setTask] = useState<Task>({
    id: "task-001",
    title: "Реализуйте функцию сортировки массива",
    description:
      "Напишите функцию sortNumbers(arr), которая возвращает новый массив с числами в порядке возрастания. Покажите время выполнения на больших массивах.",
    language: "javascript",
    template: `// Решение кандидата ниже
    function sortNumbers(arr) {
      // TODO: напишите реализацию
      return arr;
    }

    console.log(sortNumbers([3,1,2]));`,
  });

  const [value, setValue] = useState<string>(task.template);
  const [log, setLog] = useState<string[]>([]);
  const [running, setRunning] = useState(false);
  const [feedback, setFeedback] = useState<Feedback | null>(null);

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [interviewFinished, setInterviewFinished] = useState(false);

  // автоскролл чата
  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTo({
        top: chatRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages, isTyping]);

  // при смене задачи — обновляем шаблон в редакторе
  useEffect(() => {
    setValue(task.template);
  }, [task.id]);

  // старт интервью
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch("/api/start_interview", {
          method: "POST",
        });

        if (res.ok) {
          const data = await res.json();

          if (data.task) {
            setTask((prev) => ({
              ...prev,
              id: data.task.id ?? prev.id,
              title: data.task.title ?? prev.title,
              description: data.task.description ?? prev.description,
              template: data.task.template ?? prev.template,
              language: "javascript",
            }));
            setValue(data.task.template ?? task.template);
          }

          if (Array.isArray(data.messages)) {
            setMessages(
              data.messages.map((m: any, idx: number) => ({
                id: m.id ?? `srv-${idx}`,
                role: m.role === "user" ? "user" : "assistant",
                content: m.content ?? "",
              }))
            );
            return;
          }
        }
      } catch (e) {
        console.warn("start_interview error", e);
      }

      // fallback, если бэк недоступен
      setMessages([
        {
          id: "m1",
          role: "assistant",
          content:
            "Привет! Я ИИ-рекрутер. Сейчас у тебя будет серия из трёх задач по JavaScript.",
        },
        {
          id: "m2",
          role: "assistant",
          content: `Задание №1: ${task.description}`,
        },
      ]);
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleEditorMount(editor: any) {
    editorRef.current = editor;
  }

  async function onRunCode() {
    if (running) return;
    setRunning(true);
    setLog((l) => [...l, "Отправка на компиляцию..."]);

    try {
      const res = await fetch("/api/compile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          code: value,
          language: task.language,
          taskId: task.id,
        }),
      });

      if (!res.ok) {
        const text = await res.text();
        setLog((l) => [...l, `Ошибка компиляции: ${res.status} ${text}`]);
        return;
      }

      const data = await res.json();
      setLog((l) => [
        ...l,
        `Результат выполнения: ${data.stdout || data.error || "нет вывода"}`,
      ]);
    } catch (e) {
      setLog((l) => [...l, `Ошибка: ${String(e)}`]);
    } finally {
      setRunning(false);
    }
  }

  async function onDoneButton() {
    if (interviewFinished) {
      setLog((l) => [...l, "Интервью уже завершено."]);
      return;
    }

    setLog((l) => [...l, "Нажата кнопка Готово — отправляем решение ИИ..."]);
    setIsTyping(true);

    try {
      const res = await fetch("/api/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          taskId: task.id,
          code: value,
          runResult: null,
          final: true,
        }),
      });

      if (!res.ok) {
        const text = await res.text();
        setLog((l) => [...l, `Ошибка анализа: ${res.status} ${text}`]);
        setIsTyping(false);
        return;
      }

      const data = await res.json();
      setFeedback(data);

      // если бэк вернул сценарный messages + task
      if (Array.isArray(data.messages)) {
        if (data.task) {
          setTask({
            id: data.task.id,
            title: data.task.title ?? data.task.description ?? "Задание",
            description: data.task.description ?? "",
            language: "javascript",
            template: data.task.template ?? "// Новое задание\n",
          });
          setValue(data.task.template ?? "// Новое задание\n");
        }

        setMessages(
          data.messages.map((m: any, idx: number) => ({
            id: m.id ?? `srv-${idx}`,
            role: m.role === "user" ? "user" : "assistant",
            content: m.content ?? "",
          }))
        );

        if (data.report) {
          setMessages((msgs) => [
            ...msgs,
            {
              id: `ai-report-${Date.now()}`,
              role: "assistant",
              content: `Я также сформировал PDF-отчёт по интервью: ${data.report}`,
            },
          ]);
        }
      } else {
        // fallback короткий фидбек в чат
        const score = data.score ?? 0;
        const comment = data.comment ?? "Комментарий отсутствует.";
        setMessages((msgs) => [
          ...msgs,
          {
            id: `ai-feedback-${Date.now()}`,
            role: "assistant",
            content: `Анализ твоего решения:\nОценка: ${score}/100\nКомментарий: ${comment}`,
          },
        ]);
      }

      if (data.finished === true) {
        setInterviewFinished(true);
      }
    } catch (e) {
      setLog((l) => [...l, `Ошибка анализа: ${String(e)}`]);
    } finally {
      setIsTyping(false);
    }
  }

  return (
    <div className="ws-root">
      <div className="ws-shell">
        {/* Top bar */}
        <header className="ws-topbar">
          <div className="ws-topbar-left">
            <img src={logoUrl} alt="logo" className="ws-logo" />
            <div className="ws-app-info">
              <div className="ws-app-title">AI HR Assessment</div>
              <div className="ws-app-subtitle">
                Live coding interview • JavaScript
              </div>
            </div>
          </div>
          <div className="ws-topbar-right">
            <div className="ws-candidate-label">
              Кандидат: <span>Фотур Фотуров</span>
            </div>
            <div className="ws-task-label">
              Текущее задание: <span>{task.id}</span>
            </div>
          </div>
        </header>

        {/* Main layout */}
        <div className="ws-main">
          {/* LEFT: Chat + task info */}
          <section className="ws-left">
            <div className="ws-task-card">
              <div className="ws-task-header">
                <span className="ws-task-pill">Текущее задание</span>
                <span className="ws-task-id">{task.id}</span>
              </div>
              <div className="ws-task-title">{task.title}</div>
              <p className="ws-task-desc">{task.description}</p>
            </div>

            <div className="ws-chat-panel">
              <div className="ws-chat-header">
                <div className="ws-chat-title">Диалог с ИИ-рекрутером</div>
                <div className="ws-chat-status">
                  <span className="ws-status-dot" />
                  Интервью{" "}
                  {interviewFinished ? "завершено" : "в процессе"}
                </div>
              </div>

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
                      <pre className="ws-bubble-text">
                        {msg.content}
                      </pre>
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

              <div className="ws-chat-footer">
                <button
                  className="ws-btn ws-btn-secondary"
                  onClick={onRunCode}
                  disabled={running}
                >
                  {running ? "Выполняется..." : "Запустить в песочнице"}
                </button>
                <button
                  className="ws-btn ws-btn-primary"
                  onClick={onDoneButton}
                >
                  {interviewFinished
                    ? "Интервью завершено"
                    : "Готово — отправить на оценку ИИ"}
                </button>
              </div>
            </div>
          </section>

          {/* RIGHT: Editor + logs + feedback */}
          <section className="ws-right">
            <div className="ws-editor-panel">
              <div className="ws-editor-header">
                <div className="ws-editor-title">
                  Редактор решения
                  <span className="ws-editor-lang-tag">
                    {task.language.toUpperCase()}
                  </span>
                </div>
                <div className="ws-editor-file-label">
                  candidate_solution.js
                </div>
              </div>

              <div className="ws-editor-body">
                <Editor
                  height="100%"
                  defaultLanguage={task.language}
                  defaultValue={value}
                  value={value}
                  onMount={handleEditorMount}
                  onChange={(v) => setValue(v || "")}
                  theme="vs-dark"
                  options={{
                    automaticLayout: true,
                    fontSize: 14,
                    minimap: { enabled: false },
                    smoothScrolling: true,
                    scrollBeyondLastLine: false,
                  }}
                />
              </div>
            </div>

            <div className="ws-bottom-panels">
              <div className="ws-panel ws-log-panel">
                <div className="ws-panel-header">
                  <span>Логи песочницы</span>
                </div>
                <div className="ws-panel-body ws-log-body">
                  {log.length === 0 ? (
                    <div className="ws-panel-placeholder">
                      Логи появятся после запуска кода.
                    </div>
                  ) : (
                    log.map((l, i) => (
                      <div key={i} className="ws-log-line">
                        {l}
                      </div>
                    ))
                  )}
                </div>
              </div>

              <div className="ws-panel ws-feedback-panel">
                <div className="ws-panel-header">
                  <span>Фидбек / Отчёт</span>
                </div>
                <div className="ws-panel-body ws-feedback-body">
                  {!feedback && (
                    <div className="ws-panel-placeholder">
                      Оценка ещё не получена. Нажмите{" "}
                      <strong>«Готово»</strong>, чтобы отправить решение.
                    </div>
                  )}

                  {feedback && (
                    <div className="ws-feedback-content">
                      {"score" in feedback && (
                        <div className="ws-feedback-score">
                          Оценка:{" "}
                          <span>{feedback.score}/100</span>
                        </div>
                      )}
                      {"comment" in feedback && (
                        <div className="ws-feedback-comment">
                          <div className="ws-feedback-label">
                            Комментарий ИИ:
                          </div>
                          <p>{feedback.comment}</p>
                        </div>
                      )}
                      {"report" in feedback && feedback.report && (
                        <div className="ws-feedback-report">
                          <a
                            href={feedback.report}
                            target="_blank"
                            rel="noreferrer"
                          >
                            Открыть PDF-отчёт по интервью
                          </a>
                        </div>
                      )}
                      {!("report" in feedback) && (
                        <div className="ws-feedback-note">
                          Детальный отчёт хранится на сервере.
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
