"use client";

import { useEffect, useState, useRef } from "react";
import { buildApiUrl } from "@/lib/api";
import type { BoardData } from "@/lib/kanban";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

type AiSidebarProps = {
  username: string;
  board: BoardData;
  onBoardUpdate: (updatedBoard: BoardData) => void;
  onClose?: () => void;
};

const SUGGESTIONS = [
  "Add a card 'Write API docs' to Backlog",
  "Move 'Align roadmap themes' to In Progress",
  "Change the details of card-3 to 'Drafted initial dashboard layout'",
];

export const AiSidebar = ({ username, board, onBoardUpdate, onClose }: AiSidebarProps) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const storageKey = `pm-main-chat-history-${username}`;

  // Load chat history on mount
  useEffect(() => {
    try {
      const stored = sessionStorage.getItem(storageKey);
      if (stored) {
        setMessages(JSON.parse(stored) as ChatMessage[]);
      } else {
        // Initial assistant greeting
        setMessages([
          {
            role: "assistant",
            content: `Hello ${username}! I'm your Project Management Assistant. I can add, edit, or move cards for you. Try clicking one of the suggestions below or type a command!`,
          },
        ]);
      }
    } catch {
      // Fallback if sessionStorage is blocked/malformed
    }
  }, [username, storageKey]);

  // Save chat history to sessionStorage on updates
  const saveMessages = (updatedMessages: ChatMessage[]) => {
    setMessages(updatedMessages);
    try {
      sessionStorage.setItem(storageKey, JSON.stringify(updatedMessages));
    } catch {
      // Silent catch if storage fails
    }
  };

  // Scroll to bottom on new messages
  useEffect(() => {
    if (messagesEndRef.current?.scrollIntoView) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isLoading]);

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isLoading) {
      return;
    }

    const cleanText = text.trim();
    setInput("");
    setError("");

    const newMessages = [...messages, { role: "user", content: cleanText } as ChatMessage];
    saveMessages(newMessages);
    setIsLoading(true);

    try {
      const response = await fetch(buildApiUrl("/api/ai/chat"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username,
          message: cleanText,
          history: messages.slice(1), // Exclude initial greeting from prompt history context
        }),
      });

      if (!response.ok) {
        const errDetail = await response.json().catch(() => ({ detail: "Request failed" }));
        throw new Error(errDetail.detail || "Unable to contact the AI assistant.");
      }

      const data = (await response.json()) as { reply: string; board: BoardData | null };

      const finalMessages = [
        ...newMessages,
        { role: "assistant", content: data.reply } as ChatMessage,
      ];
      saveMessages(finalMessages);

      if (data.board) {
        onBoardUpdate(data.board);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error contacting the AI.";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    try {
      sessionStorage.removeItem(storageKey);
    } catch {
      // Ignore
    }
    setMessages([
      {
        role: "assistant",
        content: `Chat history cleared. How can I help you manage your board now?`,
      },
    ]);
    setError("");
  };

  return (
    <div className="flex h-full w-full flex-col rounded-[24px] border border-[var(--stroke)] bg-white shadow-[var(--shadow)] overflow-hidden">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-[var(--stroke)] bg-[var(--surface)] px-6 py-4">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-[0.15em] text-[var(--navy-dark)]">
            AI Assistant
          </h2>
          <span className="text-[10px] font-semibold text-[var(--primary-blue)]">
            Active • openai/gpt-oss-120b
          </span>
        </div>
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={handleClearChat}
            className="rounded px-2 py-1 text-[11px] font-semibold uppercase tracking-wider text-[var(--gray-text)] hover:text-[var(--secondary-purple)]"
          >
            Clear
          </button>
          {onClose && (
            <button
              type="button"
              onClick={onClose}
              className="text-[var(--navy-dark)] hover:text-[var(--primary-blue)] transition p-1"
              aria-label="Minimize Chat"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
              </svg>
            </button>
          )}
        </div>
      </header>

      {/* Messages scroll area */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4">
        {messages.map((msg, index) => {
          const isUser = msg.role === "user";
          return (
            <div
              key={index}
              className={`flex ${isUser ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                  isUser
                    ? "bg-[var(--primary-blue)] text-white rounded-br-none"
                    : "bg-[var(--surface)] text-[var(--navy-dark)] border border-[var(--stroke)] rounded-bl-none"
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          );
        })}
        {isLoading && (
          <div className="flex justify-start">
            <div className="max-w-[85%] rounded-2xl rounded-bl-none bg-[var(--surface)] border border-[var(--stroke)] px-4 py-3 text-sm text-[var(--gray-text)]">
              <span className="inline-flex gap-1">
                <span className="h-2 w-2 animate-bounce rounded-full bg-[var(--gray-text)]" style={{ animationDelay: "0ms" }} />
                <span className="h-2 w-2 animate-bounce rounded-full bg-[var(--gray-text)]" style={{ animationDelay: "150ms" }} />
                <span className="h-2 w-2 animate-bounce rounded-full bg-[var(--gray-text)]" style={{ animationDelay: "300ms" }} />
              </span>
            </div>
          </div>
        )}
        {error && (
          <div className="rounded-xl border border-red-100 bg-red-50 p-3 text-xs text-red-700">
            {error}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Preset suggestions */}
      {messages.length <= 1 && !isLoading && (
        <div className="px-5 py-2 space-y-2 border-t border-[var(--stroke)] bg-[var(--surface)]">
          <p className="text-[10px] font-bold uppercase tracking-wider text-[var(--gray-text)]">
            Suggested Actions
          </p>
          <div className="flex flex-col gap-1.5">
            {SUGGESTIONS.map((suggestion, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSendMessage(suggestion)}
                className="text-left w-full border border-[var(--stroke)] bg-white rounded-lg px-3 py-2 text-xs text-[var(--navy-dark)] hover:border-[var(--primary-blue)] hover:text-[var(--primary-blue)] transition text-ellipsis overflow-hidden whitespace-nowrap"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSendMessage(input);
        }}
        className="flex items-center border-t border-[var(--stroke)] p-3 bg-white"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask AI to make board updates..."
          disabled={isLoading}
          className="flex-1 rounded-xl border border-[var(--stroke)] px-3.5 py-2 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)] disabled:bg-gray-50"
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="ml-2 rounded-xl bg-[var(--secondary-purple)] px-4 py-2 text-sm font-semibold text-white transition hover:brightness-110 disabled:brightness-95 disabled:cursor-not-allowed"
        >
          Send
        </button>
      </form>
    </div>
  );
};
