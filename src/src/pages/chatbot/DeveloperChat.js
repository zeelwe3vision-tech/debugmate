import React, { useRef, useEffect, useState } from 'react';
import { Card, Form, Button, InputGroup } from 'react-bootstrap';
import { FaCode, FaPaperclip } from 'react-icons/fa';
import './DualChatbot.css';

const initialMockMessages = [
  { from: 'bot', text: 'Upload your code file or ask a developer question.' },
  { from: 'user', text: 'Can you review my code?' },
  { from: 'bot', text: 'Sure! Please upload your file.' },
];

const DeveloperChat = () => {
  const [messages, setMessages] = useState(initialMockMessages);
  const [input, setInput] = useState('');
  const [chatHistory, setChatHistory] = useState([
    {
      id: 1,
      summary: 'Can you review my code?...',
      fullChat: initialMockMessages,
    },
  ]);
  const [historyOpen, setHistoryOpen] = useState(true);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = (text = input) => {
    if (text.trim() === '') return;
    const newMessages = [...messages, { from: 'user', text }];
    setMessages(newMessages);
    setInput('');
    setTimeout(() => {
      const botReply = { from: 'bot', text: "I'm just a demo bot!" };
      const updatedMessages = [...newMessages, botReply];
      setMessages(updatedMessages);
      setChatHistory(prev => [
        ...prev,
        {
          id: Date.now(),
          summary: text.slice(0, 20) + '...',
          fullChat: updatedMessages,
        },
      ]);
    }, 800);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  const handleHistoryClick = (chat) => {
    setMessages(chat.fullChat);
  };

  return (
    <div className="chatbot-layout">
      {/* Toggle Button */}
      <button
        className="history-toggle-btn"
        onClick={() => setHistoryOpen(open => !open)}
        aria-label={historyOpen ? 'Hide history' : 'Show history'}
      >
        {historyOpen ? '→' : '←'}
      </button>
      {/* Main Chat Area */}
      <div className={`chatbot-container developer-chat-card${historyOpen ? ' with-history' : ' full-width'}`}> 
        <Card className="chatbot-card developer-chat-card">
          <Card.Header className="d-flex align-items-center">
            <FaCode className="me-2" /> <span>Developer Chatbot</span>
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
      <div className={`chat-history-panel1 ${historyOpen ? ' open' : ' closed'}`}>
        <h3 className='txt'>History</h3>
        {chatHistory.length === 0 ? (
          <p>No previous chats</p>
        ) : (
          chatHistory.map((chat) => (
            <div key={chat.id} className="history-item" onClick={() => handleHistoryClick(chat)}>
              {chat.summary}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default DeveloperChat; 