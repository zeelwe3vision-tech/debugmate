import React, { useState, useRef, useEffect } from 'react';
import { BsPlusCircle } from 'react-icons/bs';
import { IoSend } from 'react-icons/io5';
import { FiVideo, FiFileText, FiDatabase, FiCode } from 'react-icons/fi';
import './Communication.css';

const suggestionData = [
    
    { icon: <FiVideo />, text: 'Create video script' },
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
    const chatEndRef = useRef(null);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);
    const handleSend = (text = input) => {
        if (text.trim() === '') return;
            

        const newMessages = [...messages, { sender: 'user', text }];
        setMessages(newMessages);
        setInput('');

        setTimeout(() => {
            setMessages(prev => [...prev, { sender: 'bot', text: "I'm just a demo bot!" }]);
        }, 800);
    };

    const handleSuggestionClick = (prompt) => {
        handleSend(prompt);
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') handleSend();
    };

    return (
        <div className="page-center">
            <div className="chatbot-container">
                {messages.length === 0 ? (
                    <div id='header'>
                        <div className="chatbot-header1">Hello, there</div>
                        <div className="chatbot-subheader">How can I help you today?</div>
                    </div>
                ) : (
                    <div className="chatbot-header2">Communication</div>
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
        </div>
    );
};

export default Communication; 