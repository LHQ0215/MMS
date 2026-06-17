import React, { useState, useEffect, useRef } from "react";
import { Button, Input, Typography, Spin, Popconfirm, message as antMsg } from "antd";
import { SendOutlined, PlusOutlined, DeleteOutlined, RobotOutlined, UserOutlined, MessageOutlined } from "@ant-design/icons";
import { aiAPI } from "../../api";
import { marked } from "marked";

const { Text, Title } = Typography;
const { TextArea } = Input;

// ---------------------------------------------------------------------------
// Markdown Renderer
// ---------------------------------------------------------------------------
function MarkdownRenderer({ content }) {
  const html = marked.parse(content || "", { breaks: true, gfm: true });
  return <div className="markdown-body" dangerouslySetInnerHTML={{ __html: html }} />;
}

// ---------------------------------------------------------------------------
// Typing Indicator
// ---------------------------------------------------------------------------
function TypingIndicator() {
  return (
    <div className="chat-message assistant">
      <div className="message-avatar"><RobotOutlined /></div>
      <div className="message-bubble">
        <div className="typing-indicator">
          <span className="typing-dot" /><span className="typing-dot" /><span className="typing-dot" />
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Welcome Screen
// ---------------------------------------------------------------------------
function WelcomeScreen({ onNewChat }) {
  const suggestions = [
    "最近总是头痛，可能是什么原因？",
    "感冒了应该注意什么？",
    "如何改善睡眠质量？",
    "健康饮食有哪些建议？",
    "高血压患者在日常生活中需要注意什么？",
    "什么是低碳水饮食？",
  ];
  return (
    <div className="chat-welcome">
      <div className="welcome-icon"><RobotOutlined /></div>
      <Title level={3} style={{ margin: "16px 0 4px" }}>AI 智能助手</Title>
      <Text type="secondary" style={{ fontSize: 15, marginBottom: 28, display: "block" }}>
        您好！我可以回答健康问题和其他日常问题，随时开始对话
      </Text>
      <div className="suggestion-list">
        {suggestions.slice(0, 4).map((q, i) => (
          <Button key={i} type="default" shape="round" size="small" style={{ margin: 4 }} onClick={() => onNewChat(q)}>
            {q}
          </Button>
        ))}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Chat Page
// ---------------------------------------------------------------------------
export default function AIChatPage() {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // -- Load sessions on mount
  useEffect(() => { loadSessions(); }, []);

  // -- Load messages when session changes
  useEffect(() => {
    if (activeSessionId) loadMessages(activeSessionId);
    else setMessages([]);
  }, [activeSessionId]);

  // -- Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  const loadSessions = async () => {
    try {
      const res = await aiAPI.getChatSessions();
      setSessions(res.data || []);
    } catch (_) { /* handled by interceptor */ }
  };

  const loadMessages = async (sid) => {
    setLoading(true);
    try {
      const res = await aiAPI.getChatMessages(sid);
      setMessages(res.data || []);
    } catch (_) { setMessages([]); }
    setLoading(false);
  };

  const createNewSession = async (initialMsg) => {
    try {
      const res = await aiAPI.createChatSession({});
      const session = res.data;
      setSessions((prev) => [session, ...prev]);
      setActiveSessionId(session.id);
      setMessages([]);
      // Pre-fill input if coming from a suggestion click
      if (initialMsg) {
        setTimeout(() => setInputValue(initialMsg), 100);
      }
    } catch (_) {
      antMsg.error("创建会话失败");
    }
  };

  const deleteSession = async (sid, e) => {
    e.stopPropagation();
    try {
      await aiAPI.deleteChatSession(sid);
      setSessions((prev) => prev.filter((s) => s.id !== sid));
      if (activeSessionId === sid) setActiveSessionId(null);
    } catch (_) { antMsg.error("删除失败"); }
  };

  const sendMessage = async () => {
    const content = inputValue.trim();
    if (!content || !activeSessionId || sending) return;
    setInputValue("");
    setSending(true);

    const tempMsg = { id: Date.now(), role: "user", content };
    setMessages((prev) => [...prev, tempMsg]);

    try {
      const res = await aiAPI.sendChatMessage(activeSessionId, content);
      const { user_message, assistant_message } = res.data;
      setMessages((prev) => [
        ...prev.filter((m) => m.id !== tempMsg.id),
        { ...user_message, id: user_message.id || Date.now() },
        { ...assistant_message, id: assistant_message.id || Date.now() + 1 },
      ]);
      loadSessions(); // refresh session list for updated title
    } catch (_) {
      setMessages((prev) => prev.filter((m) => m.id !== tempMsg.id));
    }
    setSending(false);
    setTimeout(() => inputRef.current?.focus(), 50);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const fmtTime = (s) => {
    if (!s) return "";
    try { return new Date(s).toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" }); }
    catch (_) { return ""; }
  };

  return (
    <div className="ai-chat-container">
      {/* ── Sidebar ── */}
      <div className="chat-sidebar">
        <div className="sidebar-header">
          <RobotOutlined style={{ marginRight: 8 }} />
          AI 助手
        </div>
        <Button type="primary" block icon={<PlusOutlined />} onClick={() => createNewSession()}
          style={{ margin: "12px 12px 8px", width: "calc(100% - 24px)" }}>
          新对话
        </Button>
        <div className="session-list">
          {sessions.length === 0 ? (
            <div className="session-empty">
              <MessageOutlined style={{ fontSize: 22, marginBottom: 6 }} />
              <Text style={{ color: "rgba(255,255,255,0.5)", fontSize: 13 }}>暂无对话</Text>
            </div>
          ) : (
            sessions.map((s) => (
              <div key={s.id}
                className={"session-item" + (activeSessionId === s.id ? " active" : "")}
                onClick={() => setActiveSessionId(s.id)}>
                <div className="session-title">
                  <MessageOutlined style={{ marginRight: 8, fontSize: 13 }} />
                  <Text ellipsis style={{ maxWidth: 150, color: activeSessionId === s.id ? "#1677ff" : "rgba(0,0,0,0.85)", fontSize: 13 }}>
                    {s.title || "新对话"}
                  </Text>
                </div>
                <Popconfirm title="确认删除？" onConfirm={(e) => deleteSession(s.id, e)} placement="left">
                  <DeleteOutlined className="session-del" onClick={(e) => e.stopPropagation()} />
                </Popconfirm>
              </div>
            ))
          )}
        </div>
      </div>

      {/* ── Main Chat Area ── */}
      <div className="chat-main">
        {!activeSessionId ? (
          <WelcomeScreen onNewChat={createNewSession} />
        ) : (
          <>
            <div className="chat-messages">
              {loading ? (
                <div style={{ textAlign: "center", padding: 60 }}><Spin size="large" /></div>
              ) : messages.length === 0 ? (
                <div className="chat-welcome" style={{ padding: 40, minHeight: "auto" }}>
                  <div className="welcome-icon" style={{ width: 56, height: 56, fontSize: 26 }}><RobotOutlined /></div>
                  <Title level={4} style={{ margin: "10px 0 4px" }}>开始对话</Title>
                  <Text type="secondary">发送一条消息开始与 AI 交流</Text>
                </div>
              ) : (
                messages.map((m) => (
                  <div key={m.id} className={"chat-message " + m.role}>
                    <div className="message-avatar">{m.role === "user" ? <UserOutlined /> : <RobotOutlined />}</div>
                    <div className="message-bubble">
                      {m.role === "assistant" ? <MarkdownRenderer content={m.content} /> : <pre style={{ margin: 0, whiteSpace: "pre-wrap", fontFamily: "inherit", fontSize: "inherit" }}>{m.content}</pre>}
                      <div className="message-time">{fmtTime(m.created_at)}</div>
                    </div>
                  </div>
                ))
              )}
              {sending && <TypingIndicator />}
              <div ref={messagesEndRef} />
            </div>
            <div className="chat-input-area">
              <div className="chat-input-wrapper">
                <TextArea ref={inputRef} value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="输入您的问题... (Enter 发送, Shift+Enter 换行)"
                  autoSize={{ minRows: 1, maxRows: 4 }}
                  disabled={sending}
                  style={{ border: "none", boxShadow: "none", resize: "none", fontSize: 14, padding: "10px 12px", background: "transparent" }} />
                <Button type="primary" shape="circle" icon={<SendOutlined />}
                  onClick={sendMessage}
                  disabled={!inputValue.trim() || sending}
                  style={{ width: 36, height: 36, minWidth: 36, marginRight: 4, flexShrink: 0 }} />
              </div>
              <Text type="secondary" style={{ fontSize: 11, display: "block", textAlign: "center", padding: "3px 0 6px" }}>
                AI 回复仅供参考，不构成医疗诊断建议
              </Text>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
