import React from 'react';
import DeveloperChat from './DeveloperChat';
import './DualChatbot.css';

const DualChatbot = () => {
  return (
    <div className="dual-chatbot-container">
      <div className="chatbot-content">
        <DeveloperChat />
      </div>
    </div>
  );
};

export default DualChatbot; 