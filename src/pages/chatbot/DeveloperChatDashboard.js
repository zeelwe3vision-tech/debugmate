import React, { useRef, useEffect, useState } from 'react';
import { Card, Form, Button, InputGroup } from 'react-bootstrap';
import { FaCode, FaPaperclip } from 'react-icons/fa';
import './DualChatbot.css';

const initialMockMessages = [
  { from: 'bot', text: 'Upload your code file or ask a developer question.' },
  { from: 'user', text: 'Can you review my code?' },
  { from: 'bot', text: 'Sure! Please upload your file.' },
];

const DeveloperChatDashboard = () => {
  const [messages, setMessages] = useState(initialMockMessages);
  const [input, setInput] = useState('');
  const [chatHistory, setChatHistory] = useState(() => {
    const saved = localStorage.getItem('chatHistory_dashboard_wireframe');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.every(item => item.fullChat)) {
          return parsed;
        }
      } catch (e) {}
    }
    return [
      {
        id: 1,
        summary: initialMockMessages.find(m => m.from === 'user')?.text || '',
        fullChat: initialMockMessages,
      },
    ];
  });
  const [historyOpen, setHistoryOpen] = useState(true);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    localStorage.setItem('chatHistory_dashboard_wireframe', JSON.stringify(chatHistory));
  }, [chatHistory]);

  const handleSend = (text = input) => {
    if (text.trim() === '') return;
    const newMessages = [...messages, { from: 'user', text }];
    setMessages(newMessages);
    setInput('');
    setTimeout(() => {
      const botReply = { from: 'bot', text: "I'm just a demo bot!" };
      const updatedMessages = [...newMessages, botReply];
      setMessages(updatedMessages);
      // Only create a new history item if this is a new session (i.e., messages is initialMockMessages or only bot message)
      const isNewSession =
        chatHistory.length === 0 ||
        (messages.length === 1 && messages[0].from === 'bot') ||
        (messages.length === initialMockMessages.length && messages.every((m, i) => m.text === initialMockMessages[i].text && m.from === initialMockMessages[i].from));
      if (isNewSession) {
        setChatHistory(prev => [
          ...prev,
          {
            id: Date.now(),
            summary: text, // First user message as summary
            fullChat: updatedMessages,
          },
        ]);
      } else {
        // Update last history item's fullChat
        setChatHistory(prev =>
          prev.length === 0
            ? prev
            : prev.map((chat, idx) =>
                idx === prev.length - 1
                  ? { ...chat, fullChat: updatedMessages }
                  : chat
              )
        );
      }
    }, 800);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  const handleHistoryClick = (chat) => {
    setMessages(chat.fullChat);
  };

  const handleHistoryDelete = (id) => {
    setChatHistory(prev => prev.filter(chat => chat.id !== id));
  };

  const panelClass = 'dashboard-chatbot-history-panel';
  const panelTitle = 'Dashboard Chatbot History';

  return (
    <div className="chatbot-layout">
      {/* Main Chat Area */}
      <div className={`chatbot-container developer-chat-card${historyOpen ? ' with-history' : ' full-width'}`}> 
        <Card className="chatbot-card developer-chat-card">
          <Card.Header className="d-flex align-items-center">
            <FaCode className="me-2" /> <span>Dashboard Wireframe</span>
          </Card.Header>
          <Card.Body className="chat-history">
            {messages.map((msg, idx) => (
              <div key={idx} className={`chat-bubble ${msg.from}`}>{msg.text}</div>
            ))}
            <div ref={chatEndRef} />
          </Card.Body>
          <Card.Footer>
            <InputGroup>
              <Form.Label htmlFor="file-upload" className="mb-0 file-upload-label">
                <FaPaperclip />
                <Form.Control type="file" id="file-upload" className="d-none" />
              </Form.Label>
              <Form.Control
                type="text"
                placeholder="Type your message..."
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
              />
              <Button variant="primary" className="me-2" onClick={() => handleSend()}>Send</Button>
            </InputGroup>
          </Card.Footer>
        </Card>
      </div>
      {/* Chat History Sidebar */}
      <div className={`history-panel${historyOpen ? '' : ' closed'}`}> 
        <div className="panel-header">
          <h3>{panelTitle}</h3>
          <button
            className="history-toggle-btn"
            onClick={() => setHistoryOpen(false)}
            title="Close history panel"
            aria-label="Close history panel"
          >
            &rarr;
          </button>
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
                  title="Delete chat"
                >
                  ✕
                </button>
              </div>
            ))
          )}
        </div>
      </div>
      {/* Show open button when panel is closed */}
      {!historyOpen && (
        <button
          className="history-toggle-btn open-panel-btn"
          onClick={() => setHistoryOpen(true)}
          title="Open history panel"
          aria-label="Open history panel"
        >
          &larr;
        </button>
      )}
    </div>
  );
};

export default DeveloperChatDashboard; 