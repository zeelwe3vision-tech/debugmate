import React, { useState, useRef, useEffect } from 'react';
import { BsPlusCircle } from 'react-icons/bs';
import { IoSend } from 'react-icons/io5';
import { FiFileText, FiDatabase, FiCode } from 'react-icons/fi';
import './Communication.css';

const suggestionData = [
    { icon: <FiFileText />, text: 'Write a press release' },
    { icon: <FiDatabase />, text: 'Design a database schema' },
    { icon: <FiCode />, text: 'Write frontend code' },
];

const PromptSuggestions = ({ onSuggestionClick }) => (
    <div className="prompt-suggestions-container">
        <h2 className="prompt-title">Start writing with GenAI</h2>
        <div className="suggestions-grid">
            {suggestionData.map((item, index) => (
                <button key={index} className="suggestion-card" onClick={() => onSuggestionClick(item.text)}>
                    <div className="card-icon">{item.icon}</div>
                    <p className="card-text">{item.text}</p>
                </button>
            ))}
        </div>
    </div>
);

const Communication = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [chatHistory, setChatHistory] = useState(() => {
        const saved = localStorage.getItem('communication_chat_history');
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                if (Array.isArray(parsed) && parsed.every(item => item.summary && Array.isArray(item.fullChat) && item.fullChat.length > 0)) {
                    return parsed;
                }
            } catch (e) {}
        }
        return [];
    });
    const [showBgImage, setShowBgImage] = useState(false);
    const [historyOpen, setHistoryOpen] = useState(true);
    const chatEndRef = useRef(null);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    useEffect(() => {
        localStorage.setItem('communication_chat_history', JSON.stringify(chatHistory));
    }, [chatHistory]);

    const handleSend = (text = input) => {
        if (text.trim() === '') return;

        const newMessages = [...messages, { sender: 'user', text }];
        setMessages(newMessages);
        setInput('');
        setShowBgImage(true);

        setTimeout(() => {
            const botReply = { sender: 'bot', text: "I'm just a demo bot!" };
            const updatedMessages = [...newMessages, botReply];
            setMessages(updatedMessages);
            // Only create a new history item if this is a new session (i.e., messages is empty)
            const isNewSession =
                chatHistory.length === 0 || messages.length === 0;
            if (isNewSession) {
                setChatHistory(prevHist => [
                    ...prevHist,
                    {
                        id: Date.now(),
                        summary: text, // First user message as summary
                        fullChat: updatedMessages,
                    },
                ]);
            } else {
                // Update last history item's fullChat
                setChatHistory(prevHist =>
                    prevHist.length === 0
                        ? prevHist
                        : prevHist.map((chat, idx) =>
                            idx === prevHist.length - 1
                                ? { ...chat, fullChat: updatedMessages }
                                : chat
                        )
                );
            }
        }, 800);
    };

    const handleSuggestionClick = (prompt) => {
        handleSend(prompt);
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') handleSend();
    };

    const handleHistoryClick = (chat) => {
        setMessages(chat.fullChat);
        setShowBgImage(true);
    };

    const handleHistoryDelete = (id) => {
        setChatHistory(prev => prev.filter(chat => chat.id !== id));
    };

    return (
        <div className={`communication-bg ${showBgImage ? "show-bg-image" : ""}`}>
            <div className="page-center">
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
                    <div className={`chatbot-container${historyOpen ? ' with-history' : ' full-width'}`}>
                        {messages.length === 0 ? (
                            <div id='header'>
                                <div className="chatbot-header1">Hello, there</div>
                                <div className="chatbot-subheader">How can I help you today?</div>
                            </div>
                        ) : (
                            <div className='bg'>
                                <div className="chatbot-header2">Communication</div>
                            </div>
                        )}
                        <div className="chatbot-messages">
                            {messages.length === 0 ? (
                                <PromptSuggestions onSuggestionClick={handleSuggestionClick} />
                            ) : (
                                messages.map((msg, idx) => (
                                    <div key={idx} className={`message-bubble ${msg.sender}`}>
                                        <p>{msg.text}</p>
                                    </div>
                                ))
                            )}
                            <div ref={chatEndRef} />
                        </div>
                        <div className="chatbot-input-area">
                            
                            <div className="input-wrapper">
                                <button className="attach-btn">
                                    <BsPlusCircle />
                                </button>
                                <input
                                    type="text"
                                    placeholder="Type your message..."
                                    value={input}
                                    onChange={e => setInput(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                />
                            </div>
                            <button className="send-btn" onClick={() => handleSend()} >
                                <IoSend />
                            </button>
                        </div>
                    </div>
                    {/* Chat History Sidebar */}
                    <div className={`chat-history-panel${historyOpen ? ' open' : ' closed'}`}>
                        <h3 className='txt'>History</h3>
                        {chatHistory.length === 0 ? (
                            <p>No previous chats</p>
                        ) : (
                            chatHistory.filter(chat => chat.summary && Array.isArray(chat.fullChat) && chat.fullChat.length > 0).map((chat) => (
                                <div key={chat.id} className="history-item" onClick={() => handleHistoryClick(chat)} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                    <span>{chat.summary}</span>
                                    <button
                                        className="history-delete-btn"
                                        onClick={e => { e.stopPropagation(); handleHistoryDelete(chat.id); }}
                                        title="Delete chat"
                                        style={{ marginLeft: '10px', color: '#d11a2a', background: 'none', border: 'none', fontSize: '1.1rem', cursor: 'pointer' }}
                                    >
                                        ✕
                                    </button>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Communication;
