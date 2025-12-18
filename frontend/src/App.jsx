import { useState } from 'react'
import axios from 'axios'
import './App.css'

function App() {
    const [messages, setMessages] = useState([
        { role: 'system', content: 'Hello! Ask me about the weather in any city.' }
    ])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)

    const sendMessage = async () => {
        if (!input.trim()) return

        const userMessage = { role: 'user', content: input }
        setMessages(prev => [...prev, userMessage])
        setInput('')
        setLoading(true)

        try {
            const response = await axios.post('http://localhost:8000/chat', {
                message: input
            })

            const botMessage = { role: 'assistant', content: response.data.response }
            setMessages(prev => [...prev, botMessage])
        } catch (error) {
            console.error("Error sending message:", error)
            setMessages(prev => [...prev, { role: 'system', content: 'Error connecting to the server.' }])
        } finally {
            setLoading(false)
        }
    }

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            sendMessage()
        }
    }

    return (
        <div className="container">
            <header className="header">
                <h1>SanchAI Weather Bot</h1>
            </header>

            <div className="chat-container">
                <div className="messages">
                    {messages.map((msg, index) => (
                        <div key={index} className={`message ${msg.role}`}>
                            <div className="message-bubble">
                                {msg.content}
                            </div>
                        </div>
                    ))}
                    {loading && <div className="message assistant"><div className="message-bubble">Thinking...</div></div>}
                </div>

                <div className="input-area">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Ask about weather..."
                        disabled={loading}
                    />
                    <button onClick={sendMessage} disabled={loading || !input.trim()} aria-label="Send">
                        <svg viewBox="0 0 24 24">
                            <line x1="22" y1="2" x2="11" y2="13"></line>
                            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    )
}

export default App
