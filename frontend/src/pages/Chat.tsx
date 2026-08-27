import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, FileText, AlertCircle, Loader2 } from 'lucide-react'

interface Message {
    role: 'user' | 'assistant'
    content: string
    sources?: Array<{ filename: string, page?: number }>
    ticket_id?: string
}

export default function Chat() {
    const [query, setQuery] = useState('')
    const [loading, setLoading] = useState(false)
    const [messages, setMessages] = useState<Message[]>([
        { role: 'assistant', content: 'Hello! I am your AI Operations Copilot. Ask me about SOPs, policies, or report a log issue.' }
    ])
    const endRef = useRef<HTMLDivElement>(null)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!query.trim() || loading) return

        const userMsg: Message = { role: 'user', content: query }
        setMessages(prev => [...prev, userMsg])
        setQuery('')
        setLoading(true)

        try {
            const res = await fetch('http://localhost:8000/api/v1/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: userMsg.content, user_id: "00000000-0000-0000-0000-000000000000" })
            })
            const data = await res.json()

            const aiMsg: Message = {
                role: 'assistant',
                content: data.answer,
                sources: data.sources,
                ticket_id: data.ticket_id
            }
            setMessages(prev => [...prev, aiMsg])
        } catch (err) {
            setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error connecting to the backend.' }])
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    return (
        <div className="flex flex-col h-full bg-white">
            {/* Header */}
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center bg-white sticky top-0 z-10">
                <div>
                    <h2 className="text-lg font-semibold text-gray-900">Copilot Chat</h2>
                    <p className="text-sm text-gray-500">Ask questions or report incidents</p>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {messages.map((m, idx) => (
                    <div key={idx} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`flex max-w-[80%] ${m.role === 'user' ? 'flex-row-reverse' : 'flex-row'} items-start gap-3`}>
                            <div className={`h-8 w-8 rounded-full flex items-center justify-center shrink-0 ${m.role === 'user' ? 'bg-blue-600' : 'bg-green-600'}`}>
                                {m.role === 'user' ? <User size={16} className="text-white" /> : <Bot size={16} className="text-white" />}
                            </div>

                            <div className={`p-4 rounded-xl shadow-sm ${m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-800'}`}>
                                <p className="whitespace-pre-wrap">{m.content}</p>

                                {m.sources && m.sources.length > 0 && (
                                    <div className="mt-3 pt-3 border-t border-gray-200/20 grid gap-2">
                                        <p className="text-xs font-semibold opacity-70 flex items-center gap-1">
                                            <FileText size={12} /> Sources:
                                        </p>
                                        {m.sources.map((src, i) => (
                                            <div key={i} className="text-xs opacity-80 bg-black/5 p-1.5 rounded truncate">
                                                {src.filename} {src.page ? `(p. ${src.page})` : ''}
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {m.ticket_id && (
                                    <div className="mt-3 bg-yellow-50 text-yellow-800 p-2 rounded text-xs flex items-center gap-2 border border-yellow-200">
                                        <AlertCircle size={14} />
                                        <span>Ticket Created: {m.ticket_id}</span>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex justify-start">
                        <div className="flex items-center gap-2 text-gray-400 bg-gray-50 px-4 py-2 rounded-lg">
                            <Loader2 size={16} className="animate-spin" /> Thinking...
                        </div>
                    </div>
                )}
                <div ref={endRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t border-gray-200 bg-gray-50">
                <form onSubmit={handleSubmit} className="flex gap-2 max-w-4xl mx-auto">
                    <input
                        value={query}
                        onChange={e => setQuery(e.target.value)}
                        placeholder="Ask about a policy or report an error..."
                        className="flex-1 px-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
                    />
                    <button
                        disabled={loading}
                        type="submit"
                        className="bg-blue-600 text-white px-6 py-2 rounded-xl hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-2 font-medium"
                    >
                        <Send size={18} /> Send
                    </button>
                </form>
            </div>
        </div>
    )
}
