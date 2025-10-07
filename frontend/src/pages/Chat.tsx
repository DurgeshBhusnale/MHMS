import React, { useEffect, useMemo, useRef, useState } from 'react';
import apiService from '../services/api';
import { v4 as uuidv4 } from 'uuid';

interface ChatTurn {
  role: 'user' | 'bot';
  message: string;
  emotion?: string | null;
  sentiment?: string | null;
  timestamp?: string;
}

const SentimentBadge: React.FC<{ label?: string | null }> = ({ label }) => {
  if (!label) return null;
  const map: Record<string, string> = {
    POSITIVE: 'bg-green-100 text-green-700 border-green-300',
    NEGATIVE: 'bg-red-100 text-red-700 border-red-300',
    NEUTRAL: 'bg-gray-100 text-gray-700 border-gray-300',
    joy: 'bg-green-100 text-green-700 border-green-300',
    sadness: 'bg-blue-100 text-blue-700 border-blue-300',
    anger: 'bg-red-100 text-red-700 border-red-300',
    fear: 'bg-yellow-100 text-yellow-700 border-yellow-300',
    disgust: 'bg-purple-100 text-purple-700 border-purple-300',
    surprise: 'bg-amber-100 text-amber-700 border-amber-300',
  };
  const cls = map[label] || 'bg-gray-100 text-gray-700 border-gray-300';
  return <span className={`px-2 py-0.5 text-xs rounded border ${cls}`}>{label}</span>;
};

const Chat: React.FC = () => {
  const [sessionId, setSessionId] = useState<string>('');
  const [input, setInput] = useState('');
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [loading, setLoading] = useState(false);
  const [ready, setReady] = useState<boolean | null>(null);
  const [error, setError] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement | null>(null);

  const ensureSession = (): string => {
    let sid = localStorage.getItem('chat_session_id') || '';
    if (!sid) {
      sid = uuidv4();
      localStorage.setItem('chat_session_id', sid);
    }
    setSessionId(sid);
    return sid;
  };

  useEffect(() => {
    const sid = ensureSession();
    // health check
    apiService.getChatHealth()
      .then((res) => {
        const status = res.data?.status;
        setReady(status === 'healthy' || status === 'degraded');
        setError(status === 'unhealthy' ? res.data?.error || 'Chat service is unhealthy' : null);
      })
      .catch(() => setReady(true));

    // Note: New AI chat service doesn't have history endpoint that returns chat format
    // Starting with empty conversation for now
    setTurns([]);
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [turns, loading]);

  const placeholder = useMemo(() => (
    ready === false ? 'AI chat service is loading…' : 'Share how you\'re feeling today...'
  ), [ready]);

  const send = async () => {
    if (!input.trim() || loading) return;
    const text = input.trim();
    setInput('');
  const sid = sessionId || ensureSession();

    const userTurn: ChatTurn = { role: 'user', message: text, timestamp: new Date().toISOString() };
    setTurns((t) => [...t, userTurn]);
    setLoading(true);
    try {
      const res = await apiService.sendChatMessage(sid, text);
      const reply = (res.data?.response || '').toString();
      // New AI chat service doesn't return emotion/sentiment analysis
      // Focus on empathetic conversation instead
      const botTurn: ChatTurn = { role: 'bot', message: reply, timestamp: new Date().toISOString() };
      setTurns((t) => [...t, botTurn]);
      // Emergency handling is built into the AI chat service responses
    } catch (e: any) {
      if (e?.response?.status === 401) {
        window.location.href = '/login';
        return;
      }
      setError(e?.message || 'Network error. Please make sure you are logged in.');
    } finally {
      setLoading(false);
    }
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* top bar */}
      <header className="sticky top-0 z-10 backdrop-blur supports-[backdrop-filter]:bg-white/60 bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-gradient-to-br from-black via-gray-700 to-gray-900" />
            <h1 className="text-sm md:text-base font-semibold text-gray-800">SATHI AI Chat - Mental Health Support</h1>
          </div>
          <div className="text-xs text-gray-500">Session: {sessionId.slice(0, 8)}</div>
        </div>
      </header>

      {/* body */}
      <main className="max-w-3xl mx-auto px-4 pt-6 pb-28">
        {/* notice */}
        {ready === false && (
          <div className="mb-4 rounded-md border border-yellow-300 bg-yellow-50 p-3 text-sm text-yellow-800">
            Chat service is loading. Please wait a moment … {error ? `(${error})` : ''}
          </div>
        )}
        {!!error && ready !== false && (
          <div className="mb-4 rounded-md border border-red-300 bg-red-50 p-3 text-sm text-red-800">
            {error}
          </div>
        )}

        {/* chat list */}
        <div className="space-y-4">
          {turns.map((t, idx) => (
            <div key={idx} className={`flex ${t.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] rounded-2xl px-4 py-3 border shadow-sm ${t.role === 'user' ? 'bg-gray-900 text-white border-gray-800' : 'bg-white text-gray-800 border-gray-200'}`}>
                <div className="text-sm whitespace-pre-wrap leading-relaxed">{t.message}</div>
                {/* New AI chat service provides empathetic responses without separate emotion/sentiment badges */}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="max-w-[85%] rounded-2xl px-4 py-3 border bg-white text-gray-800 border-gray-200 shadow-sm">
                <div className="text-sm animate-pulse">AI counselor is responding…</div>
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>
      </main>

      {/* input dock */}
      <div className="fixed bottom-0 left-0 right-0 border-t border-gray-200 bg-white/90 backdrop-blur">
        <div className="max-w-3xl mx-auto px-4 py-3">
          <div className="flex gap-2">
            <input
              className="flex-1 rounded-xl border border-gray-300 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-gray-900"
              placeholder={placeholder}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onKeyDown}
              disabled={ready === false}
            />
            <button
              onClick={send}
              disabled={!input.trim() || loading || ready === false}
              className="rounded-xl bg-gray-900 text-white px-5 py-3 text-sm font-medium hover:bg-black disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;
