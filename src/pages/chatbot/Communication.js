// // ✅ Communication.js (Fully updated to ensure session is respected)
// import React, { useState, useRef, useContext, useEffect } from 'react';
// import ReactMarkdown from 'react-markdown';
// import { MyContext } from '../../App';

// function Communication() {
//   const { userEmail } = useContext(MyContext);
//   const [messages, setMessages] = useState([]);
//   const [inputText, setInputText] = useState('');
//   const chatEndRef = useRef(null);

//   useEffect(() => {
//     if (userEmail) {
//       fetch("http://localhost:5000/set_session", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         credentials: "include", // ⬅️ IMPORTANT
//         body: JSON.stringify({ email: userEmail })
//       })
//       .then(res => {
//         if (!res.ok) throw new Error("Failed to set session in Flask");
//       })
//       .catch(console.error);
//     }
//   }, [userEmail]);

//   const sendMessage = async () => {
//     if (inputText.trim() === '') return;
//     setMessages(prev => [...prev, { role: 'user', content: inputText }]);

//     try {
//       const response = await fetch('http://localhost:5000/chat', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         credentials: 'include', // ⬅️ Ensure session cookie is sent
//         body: JSON.stringify({ message: inputText })
//       });

//       const data = await response.json();
//       setMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);
//     } catch (err) {
//       console.error('Chat error:', err);
//       setMessages(prev => [...prev, { role: 'assistant', content: 'Error connecting to chatbot.' }]);
//     }

//     setInputText('');
//   };

//   return (
//     <div style={styles.container}>
//       <div style={styles.chatBox}>
//         {messages.map((msg, i) => (
//           <div key={i} style={msg.role === 'user' ? styles.userMsg : styles.botMsg}>
//             <strong>{msg.role === 'user' ? 'You' : 'Bot'}:</strong>
//             <ReactMarkdown>{msg.content}</ReactMarkdown>
//           </div>
//         ))}
//         <div ref={chatEndRef} />
//       </div>
//       <div style={styles.inputArea}>
//         <input
//           style={styles.input}
//           type="text"
//           value={inputText}
//           onChange={(e) => setInputText(e.target.value)}
//           placeholder="Type a message..."
//         />
//         <button style={styles.button} onClick={sendMessage}>Send</button>
//       </div>
//     </div>
//   );
// }

// const styles = {
//   container: {
//     maxWidth: '600px',
//     margin: '40px auto',
//     border: '1px solid #ccc',
//     borderRadius: '8px',
//     padding: '20px',
//     backgroundColor: '#f9f9f9',
//     fontFamily: 'Arial',
//   },
//   chatBox: {
//     maxHeight: '400px',
//     overflowY: 'auto',
//     marginBottom: '15px',
//   },
//   userMsg: {
//     textAlign: 'right',
//     margin: '10px 0',
//     color: '#0a67ca',
//   },
//   botMsg: {
//     textAlign: 'left',
//     margin: '10px 0',
//     color: '#333',
//   },
//   inputArea: {
//     display: 'flex',
//     gap: '10px',
//   },
//   input: {
//     flex: 1,
//     padding: '10px',
//     fontSize: '16px',
//   },
//   button: {
//     padding: '10px 20px',
//     fontSize: '16px',
//     cursor: 'pointer',
//     backgroundColor: '#0a67ca',
//     color: '#fff',
//     border: 'none',
//     borderRadius: '4px',
//   }
// };
import React, { useState, useEffect, useRef, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { MyContext } from '../../App';

function Communication() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const chatEndRef = useRef(null);

  const navigate = useNavigate();
  const context = useContext(MyContext);
  const userEmail = context.userEmail;
  const userName = context.username || '';

  // Redirect if no user email (run only once or when userEmail changes)
  useEffect(() => {
    if (!userEmail) {
      navigate('/login');
    }
  }, [userEmail, navigate]);

  // Set backend session on mount or when userEmail changes
  useEffect(() => {
    if (userEmail) {
      fetch('http://localhost:5000/set_session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email: userEmail, name: userName }),
      })
        .then(res => res.json())
        .then(data => console.log('Session set:', data))
        .catch(console.error);
    }
  }, [userEmail, userName]);

  // Auto scroll on new messages
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Sending a message (no hooks inside here)
  const sendMessage = async () => {
    if (inputText.trim() === '') return;
    setMessages(prev => [...prev, { role: 'user', content: inputText }]);

    try {
      const response = await fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ message: inputText }),
      });
      const data = await response.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Error connecting to chatbot.' }]);
    }
    setInputText('');
  };

  return (
    <div style={styles.container}>
      <h3>Chatbot</h3>
      <div style={styles.chatBox}>
        {messages.map((msg, i) => (
          <div key={i} style={msg.role === 'user' ? styles.userMsg : styles.botMsg}>
            <strong>{msg.role === 'user' ? 'You' : 'Bot'}:</strong>
            <ReactMarkdown>{msg.content}</ReactMarkdown>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>
      <div style={styles.inputArea}>
        <input
          style={styles.input}
          type="text"
          value={inputText}
          onChange={e => setInputText(e.target.value)}
          placeholder="Type a message..."
          onKeyDown={e => { if (e.key === 'Enter') sendMessage(); }}
        />
        <button style={styles.button} onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

const styles = {
  container: { maxWidth: 600, margin: '40px auto', border: '1px solid #ccc', borderRadius: 8, padding: 20, backgroundColor: '#f9f9f9', fontFamily: 'Arial' },
  chatBox: { maxHeight: 400, overflowY: 'auto', marginBottom: 15 },
  userMsg: { textAlign: 'right', margin: '10px 0', color: '#0a67ca' },
  botMsg: { textAlign: 'left', margin: '10px 0', color: '#333' },
  inputArea: { display: 'flex', gap: 10 },
  input: { flex: 1, padding: 10, fontSize: 16 },
  button: { padding: '10px 20px', fontSize: 16, cursor: 'pointer', backgroundColor: '#0a67ca', color: '#fff', border: 'none', borderRadius: 4 },
};

export default Communication;
