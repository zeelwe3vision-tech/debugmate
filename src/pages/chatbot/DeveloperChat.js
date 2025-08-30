
import React, { useRef, useEffect, useState } from 'react';
import { Card } from 'react-bootstrap';
import { FaCode, FaPaperclip } from 'react-icons/fa';
import './DualChatbot.css';
import { useContext } from 'react';
import { MyContext } from '../../App';


const getInitialMessages = (projectInfo) => {
  if (projectInfo.projectId) {
    return [
      { from: 'bot', text: `Hello! I'm here to help you with your project "${projectInfo.projectName}". You can ask me questions about development, code review, or upload files for analysis.` },
    ];
  }
  return [
    { from: 'bot', text: 'Upload your code file or ask a developer question.' },
  ];
};

const DeveloperChat = ({ projectInfo = {} }) => {
  const [messages, setMessages] = useState(getInitialMessages(projectInfo));
  const [input, setInput] = useState('');
  const chatEndRef = useRef(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [historyOpen, setHistoryOpen] = useState(true);
  const [sessionActive, setSessionActive] = useState(false);
  const context = useContext(MyContext);
  const userEmail = context.userEmail;
  const userName = context.userName || "User";
  const userRole = context.userRole || "employee";
  
  // Auto-scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Save to localStorage per project
  const storageKey = projectInfo.projectId
    ? `chatHistory_project_${projectInfo.projectId}`
    : 'chatHistory_web_designing_prototyping';

  useEffect(() => {
    localStorage.setItem(storageKey, JSON.stringify(chatHistory));
  }, [chatHistory, storageKey]);

  // Restore last chat
  useEffect(() => {
    const saved = localStorage.getItem(storageKey);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed)) {
          setChatHistory(parsed);
          const last = parsed[parsed.length - 1];
          if (last?.fullChat) setMessages(last.fullChat);
        }
      } catch (e) {
        console.error("Failed to parse chat history", e);
      }
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);


  // Set session once DualChat mounts
useEffect(() => {
  const setSession = async () => {
    if (!userEmail) return;
    try {
      await fetch("http://localhost:5000/set_session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email: userEmail, name: userName })
      });
      console.log("✅ Session set for Dual Chat");
    } catch (error) {
      console.error("❌ Failed to set session:", error);
    }
  };
  setSession();
}, [userEmail, userName]);


  // 🔑 Send message to Flask backend
  const handleSend = async (text = input) => {
    if (text.trim() === '') return;

    const newMessages = [...messages, { from: 'user', text }];
    setMessages(newMessages);
    setInput('');
    setSessionActive(true);

    try {
      const response = await fetch("http://localhost:5000/chat/dual", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          message: text,   // 🔑 use "message" (your Flask route checks this)
          project_id: projectInfo?.projectId || "default"
        }),
      });
      
      console.log("📤 Sending payload:", {
        message: text,
        project_id: projectInfo?.projectId || "default"
      });
      
      const data = await response.json();
      const botReply = { from: 'bot', text: data.reply || "⚠️ No reply from server" };

      const updatedMessages = [...newMessages, botReply];
      setMessages(updatedMessages);

      // Save chat thread
      if (projectInfo.projectId) {
        setChatHistory(prev => {
          if (!prev || prev.length === 0) {
            return [{ id: projectInfo.projectId, summary: text, fullChat: updatedMessages }];
          }
          return prev.map((chat, idx) =>
            idx === prev.length - 1
              ? { ...chat, summary: chat.summary || text, fullChat: updatedMessages }
              : chat
          );
        });
      } else {
        if (!sessionActive) {
          setChatHistory(prev => [
            ...prev,
            { id: Date.now(), summary: text, fullChat: updatedMessages },
          ]);
        } else {
          setChatHistory(prev =>
            prev.map((chat, idx) =>
              idx === prev.length - 1 ? { ...chat, fullChat: updatedMessages } : chat
            )
          );
        }
      }
    } catch (error) {
      console.error("❌ Chat request failed:", error);
      setMessages(prev => [...prev, { from: 'bot', text: "Error connecting to chatbot." }]);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  const handleNewChat = () => {
    setMessages(getInitialMessages(projectInfo));
    setSessionActive(false);
    if (projectInfo.projectId) {
      setChatHistory(prev =>
        prev.map((chat, idx) =>
          idx === prev.length - 1 ? { ...chat, fullChat: getInitialMessages(projectInfo) } : chat
        )
      );
    }
  };

  const handleHistoryClick = (chat) => {
    setMessages(chat.fullChat);
  };

  const handleHistoryDelete = (id) => {
    setChatHistory(prev => prev.filter(chat => chat.id !== id));
  };  return (
    <div className="chatbot-layout">
      {/* Main Chat Area */}
      <div className={`chatbot-container developer-chat-card${historyOpen ? ' with-history' : ' full-width'}`}>
        <Card className="chatbot-card developer-chat-card">
          <Card.Header className="d-flex align-items-center">
            <FaCode className="me-2" /> <span>Developer Chatbot</span>
          </Card.Header>

          {projectInfo.projectId && (
            <div className="project-info-banner" style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              padding: '12px 20px',
              fontSize: '14px',
              borderBottom: '1px solid #e9ecef'
            }}>
              <strong>Project:</strong> {projectInfo.projectName || 'Unknown Project'}
              {projectInfo.projectId && <span style={{ marginLeft: '10px', opacity: 0.8 }}>(ID: {projectInfo.projectId})</span>}
            </div>
          )}

          <Card.Body className="chat-history">
            {messages.map((msg, idx) => (
              <div key={idx} className={`chat-bubble ${msg.from}`}>{msg.text}</div>
            ))}
            <div ref={chatEndRef} />
          </Card.Body>

          <Card.Footer>
            <div className="chatbot-input-area">
              <div className="input-wrapper">
                <button className="attach-btn"><FaPaperclip /></button>
                <input
                  type="text"
                  placeholder="Type your message..."
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                />
                <button className="send-btn" onClick={() => handleSend()}>Send</button>
              </div>
            </div>
          </Card.Footer>
        </Card>
      </div>

      {/* History Panel */}
      <div className={`history-panel${historyOpen ? '' : ' closed'}`}>
        <div className="panel-header">
          <h3>Chat History</h3>
          <button onClick={() => setHistoryOpen(false)} className="history-toggle-btn">&rarr;</button>
        </div>
        <div className="history-list">
          {chatHistory.length === 0 ? (
            <p style={{ color: '#888', fontStyle: 'italic' }}>No previous chats</p>
          ) : (
            chatHistory.map((chat) => (
              <div
                key={chat.id}
                className={`history-item${messages === chat.fullChat ? ' selected' : ''}`}
                onClick={() => handleHistoryClick(chat)}
                style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
              >
                <span className="history-summary">{chat.summary}</span>
                <button
                  className="history-delete-btn"
                  onClick={e => { e.stopPropagation(); handleHistoryDelete(chat.id); }}
            >
                  ✕
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {!historyOpen && (
        <button className="history-toggle-btn open-panel-btn" onClick={() => setHistoryOpen(true)}>&larr;</button>
      )}
    </div>
  );
};

export default DeveloperChat;
