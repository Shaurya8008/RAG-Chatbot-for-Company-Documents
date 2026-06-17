"use client";

import { useState, useRef, useEffect, useCallback, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import {
  Send,
  Sparkles,
  ArrowLeft,
  FileText,
  ChevronRight,
  X,
  AlertCircle,
  CheckCircle2,
  Clock,
  Loader2,
  BookOpen,
  Search,
  Filter,
  MessageSquare,
  Plus,
} from "lucide-react";
import { sendChatQuery, type ChatResponse, type Citation } from "@/lib/api";

/* ── Types ── */
interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  confidence?: string;
  retrievalMetadata?: Record<string, unknown>;
  generationMetadata?: Record<string, unknown>;
  isLoading?: boolean;
}

/* ── Retrieval State Labels ── */
const RETRIEVAL_STATES = [
  { label: "Searching documents...", icon: Search, duration: 800 },
  { label: "Reranking sources...", icon: Filter, duration: 1200 },
  { label: "Drafting grounded answer...", icon: Sparkles, duration: 600 },
];

/* ── Confidence Badge ── */
function ConfidenceBadge({ confidence }: { confidence: string }) {
  const config: Record<string, { color: string; bg: string; label: string }> = {
    high: { color: "var(--confidence-high)", bg: "var(--success-bg)", label: "High confidence" },
    medium: { color: "var(--confidence-medium)", bg: "var(--warning-bg)", label: "Medium confidence" },
    low: { color: "var(--confidence-low)", bg: "var(--error-bg)", label: "Low confidence" },
    no_results: { color: "var(--text-tertiary)", bg: "var(--surface-secondary)", label: "No sources found" },
  };
  const c = config[confidence] || config.low;

  return (
    <span
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium"
      style={{ background: c.bg, color: c.color }}
    >
      {confidence === "high" ? (
        <CheckCircle2 size={12} />
      ) : confidence === "no_results" ? (
        <AlertCircle size={12} />
      ) : (
        <Clock size={12} />
      )}
      {c.label}
    </span>
  );
}

/* ── Citation Chip ── */
function CitationChip({
  citation,
  onClick,
  index,
}: {
  citation: Citation;
  onClick: () => void;
  index: number;
}) {
  return (
    <motion.button
      initial={{ opacity: 0, scale: 0.9, y: 8 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.3 }}
      onClick={onClick}
      className="group flex items-center gap-2 px-3 py-2 rounded-lg text-left transition-all text-sm"
      style={{
        background: "var(--surface-secondary)",
        border: "1px solid var(--border)",
      }}
      whileHover={{
        borderColor: "var(--accent)",
        background: "var(--accent-lighter)",
      }}
    >
      <FileText
        size={14}
        className="flex-shrink-0"
        style={{ color: "var(--accent)" }}
      />
      <span className="truncate" style={{ color: "var(--text-primary)" }}>
        {citation.document_title}
      </span>
      {citation.section_title && (
        <>
          <ChevronRight size={12} style={{ color: "var(--text-tertiary)" }} />
          <span
            className="truncate text-xs"
            style={{ color: "var(--text-secondary)" }}
          >
            {citation.section_title}
          </span>
        </>
      )}
    </motion.button>
  );
}

/* ── Source Drawer ── */
function SourceDrawer({
  citation,
  onClose,
}: {
  citation: Citation | null;
  onClose: () => void;
}) {
  return (
    <AnimatePresence>
      {citation && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40"
            style={{ background: "rgba(0,0,0,0.3)" }}
            onClick={onClose}
          />
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 30, stiffness: 300 }}
            className="fixed right-0 top-0 bottom-0 w-full max-w-lg z-50 overflow-y-auto"
            style={{
              background: "var(--surface)",
              borderLeft: "1px solid var(--border)",
              boxShadow: "var(--shadow-xl)",
            }}
          >
            {/* Header */}
            <div
              className="sticky top-0 flex items-center justify-between p-5"
              style={{
                background: "var(--surface)",
                borderBottom: "1px solid var(--border)",
              }}
            >
              <div className="flex items-center gap-3">
                <div
                  className="w-9 h-9 rounded-lg flex items-center justify-center"
                  style={{
                    background: "var(--accent-lighter)",
                    color: "var(--accent)",
                  }}
                >
                  <BookOpen size={18} />
                </div>
                <div>
                  <h3
                    className="font-semibold text-sm"
                    style={{ color: "var(--text-primary)" }}
                  >
                    Source Document
                  </h3>
                  <p
                    className="text-xs"
                    style={{ color: "var(--text-secondary)" }}
                  >
                    Retrieved evidence
                  </p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 rounded-lg transition-colors"
                style={{ color: "var(--text-secondary)" }}
              >
                <X size={18} />
              </button>
            </div>

            {/* Content */}
            <div className="p-6 space-y-5">
              <div>
                <p
                  className="text-xs font-medium uppercase tracking-wider mb-1.5"
                  style={{ color: "var(--text-tertiary)" }}
                >
                  Document
                </p>
                <p
                  className="font-semibold"
                  style={{ color: "var(--text-primary)" }}
                >
                  {citation.document_title}
                </p>
              </div>

              {citation.section_title && (
                <div>
                  <p
                    className="text-xs font-medium uppercase tracking-wider mb-1.5"
                    style={{ color: "var(--text-tertiary)" }}
                  >
                    Section
                  </p>
                  <p style={{ color: "var(--text-primary)" }}>
                    {citation.section_title}
                  </p>
                </div>
              )}

              {citation.parent_section && (
                <div>
                  <p
                    className="text-xs font-medium uppercase tracking-wider mb-1.5"
                    style={{ color: "var(--text-tertiary)" }}
                  >
                    Parent Section
                  </p>
                  <p style={{ color: "var(--text-secondary)" }}>
                    {citation.parent_section}
                  </p>
                </div>
              )}

              <div>
                <p
                  className="text-xs font-medium uppercase tracking-wider mb-1.5"
                  style={{ color: "var(--text-tertiary)" }}
                >
                  Relevance Score
                </p>
                <div className="flex items-center gap-2">
                  <div
                    className="h-2 rounded-full flex-1"
                    style={{ background: "var(--surface-tertiary)" }}
                  >
                    <div
                      className="h-2 rounded-full"
                      style={{
                        width: `${Math.min(citation.relevance_score * 100, 100)}%`,
                        background: "var(--accent)",
                      }}
                    />
                  </div>
                  <span
                    className="text-sm font-mono"
                    style={{ color: "var(--text-secondary)" }}
                  >
                    {(citation.relevance_score * 100).toFixed(1)}%
                  </span>
                </div>
              </div>

              <div>
                <p
                  className="text-xs font-medium uppercase tracking-wider mb-2"
                  style={{ color: "var(--text-tertiary)" }}
                >
                  Excerpt
                </p>
                <div
                  className="p-4 rounded-xl text-sm leading-relaxed"
                  style={{
                    background: "var(--surface-secondary)",
                    color: "var(--text-primary)",
                    borderLeft: "3px solid var(--accent)",
                  }}
                >
                  {citation.excerpt}
                </div>
              </div>

              <div
                className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs"
                style={{
                  background: "var(--surface-secondary)",
                  color: "var(--text-tertiary)",
                }}
              >
                <FileText size={12} />
                Access: {citation.permission_level.replace("_", " ")}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

/* ── Loading State ── */
function RetrievalLoader() {
  const [stateIndex, setStateIndex] = useState(0);

  useEffect(() => {
    const timers: NodeJS.Timeout[] = [];
    let cumulative = 0;
    RETRIEVAL_STATES.forEach((state, i) => {
      if (i > 0) {
        cumulative += RETRIEVAL_STATES[i - 1].duration;
        timers.push(setTimeout(() => setStateIndex(i), cumulative));
      }
    });
    return () => timers.forEach(clearTimeout);
  }, []);

  const current = RETRIEVAL_STATES[stateIndex];
  const Icon = current.icon;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex items-center gap-3 py-4"
    >
      <div className="flex items-center gap-2" style={{ color: "var(--accent)" }}>
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        >
          <Loader2 size={16} />
        </motion.div>
      </div>
      <AnimatePresence mode="wait">
        <motion.span
          key={stateIndex}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          className="text-sm"
          style={{ color: "var(--text-secondary)" }}
        >
          <Icon size={14} className="inline mr-1.5" />
          {current.label}
        </motion.span>
      </AnimatePresence>
    </motion.div>
  );
}

/* ── Empty State ── */
function EmptyState() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="flex flex-col items-center justify-center h-full text-center px-6"
    >
      <div
        className="w-16 h-16 rounded-2xl flex items-center justify-center mb-6"
        style={{ background: "var(--accent-lighter)", color: "var(--accent)" }}
      >
        <MessageSquare size={28} />
      </div>
      <h2
        className="text-2xl font-bold mb-2"
        style={{ color: "var(--text-primary)" }}
      >
        Acme Knowledge Assistant
      </h2>
      <p
        className="text-sm max-w-md mb-8 leading-relaxed"
        style={{ color: "var(--text-secondary)" }}
      >
        Ask questions about HR policies, onboarding procedures, benefits,
        company guidelines, and more. Every answer is grounded in approved
        company documents.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-xl w-full">
        {[
          "How many PTO days do new employees get?",
          "What benefits start on day one?",
          "What is the remote work policy?",
          "How does the 401(k) match work?",
        ].map((q, i) => (
          <motion.button
            key={i}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 + i * 0.08 }}
            className="text-left p-4 rounded-xl text-sm transition-all"
            style={{
              background: "var(--surface)",
              border: "1px solid var(--border)",
              color: "var(--text-primary)",
            }}
            onClick={() => {
              const event = new CustomEvent("prefill-query", {
                detail: { query: q },
              });
              window.dispatchEvent(event);
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = "var(--accent)";
              e.currentTarget.style.boxShadow = "var(--shadow-sm)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = "var(--border)";
              e.currentTarget.style.boxShadow = "none";
            }}
          >
            {q}
          </motion.button>
        ))}
      </div>
    </motion.div>
  );
}

/* ── Main Chat Component ── */
function ChatPageContent() {
  const searchParams = useSearchParams();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Handle pre-filled query from URL
  useEffect(() => {
    const q = searchParams.get("q");
    if (q && messages.length === 0) {
      setInput(q);
      // Auto-submit after a short delay
      setTimeout(() => handleSubmit(q), 300);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  // Handle prefill events from empty state
  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      if (detail?.query) {
        setInput(detail.query);
        inputRef.current?.focus();
      }
    };
    window.addEventListener("prefill-query", handler);
    return () => window.removeEventListener("prefill-query", handler);
  }, []);

  const handleSubmit = async (overrideQuery?: string) => {
    const query = overrideQuery || input.trim();
    if (!query || isLoading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: query,
    };

    const loadingMessage: Message = {
      id: `loading-${Date.now()}`,
      role: "assistant",
      content: "",
      isLoading: true,
    };

    setMessages((prev) => [...prev, userMessage, loadingMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response: ChatResponse = await sendChatQuery(
        query,
        sessionId || undefined
      );

      if (!sessionId) {
        setSessionId(response.session_id);
      }

      const assistantMessage: Message = {
        id: response.message_id,
        role: "assistant",
        content: response.answer,
        citations: response.citations,
        confidence: response.confidence,
        retrievalMetadata: response.retrieval_metadata,
        generationMetadata: response.generation_metadata,
      };

      setMessages((prev) =>
        prev.map((m) => (m.isLoading ? assistantMessage : m))
      );
    } catch (error) {
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: "assistant",
        content:
          "I'm sorry, I couldn't process your request. Please make sure the backend is running (`python -m app.main` in the backend directory) and Ollama is running with the required models.",
        confidence: "low",
      };
      setMessages((prev) =>
        prev.map((m) => (m.isLoading ? errorMessage : m))
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div
      className="flex h-screen"
      style={{ background: "var(--background)" }}
    >
      {/* ── Main Chat Area ── */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between px-6 py-4"
          style={{ borderBottom: "1px solid var(--border)" }}
        >
          <div className="flex items-center gap-4">
            <Link
              href="/"
              className="p-2 rounded-lg transition-colors"
              style={{ color: "var(--text-secondary)" }}
            >
              <ArrowLeft size={18} />
            </Link>
            <div className="flex items-center gap-2.5">
              <div
                className="w-8 h-8 rounded-lg flex items-center justify-center"
                style={{
                  background: "var(--accent)",
                  color: "var(--text-inverse)",
                }}
              >
                <Sparkles size={16} />
              </div>
              <div>
                <h1
                  className="font-semibold text-sm"
                  style={{ color: "var(--text-primary)" }}
                >
                  Knowledge Assistant
                </h1>
                <p className="text-xs" style={{ color: "var(--text-secondary)" }}>
                  HR Policy & Onboarding
                </p>
              </div>
            </div>
          </div>
          <button
            onClick={() => {
              setMessages([]);
              setSessionId(null);
            }}
            className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors"
            style={{
              color: "var(--text-secondary)",
              border: "1px solid var(--border)",
            }}
          >
            <Plus size={14} />
            New Chat
          </button>
        </motion.header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-6">
          {messages.length === 0 ? (
            <EmptyState />
          ) : (
            <div className="max-w-3xl mx-auto space-y-6">
              <AnimatePresence mode="popLayout">
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className={`flex ${
                      message.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    {message.role === "user" ? (
                      /* User message */
                      <div
                        className="max-w-[80%] px-5 py-3.5 rounded-2xl rounded-br-md text-sm leading-relaxed"
                        style={{
                          background: "var(--accent)",
                          color: "var(--text-inverse)",
                        }}
                      >
                        {message.content}
                      </div>
                    ) : message.isLoading ? (
                      /* Loading state */
                      <div className="max-w-[85%] w-full">
                        <RetrievalLoader />
                      </div>
                    ) : (
                      /* Assistant message */
                      <div className="max-w-[85%] w-full space-y-3">
                        <motion.div
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ duration: 0.4 }}
                          className="p-5 rounded-2xl rounded-bl-md"
                          style={{
                            background: "var(--surface)",
                            border: "1px solid var(--border)",
                          }}
                        >
                          {/* Confidence badge */}
                          {message.confidence && (
                            <div className="mb-3">
                              <ConfidenceBadge
                                confidence={message.confidence}
                              />
                            </div>
                          )}

                          {/* Answer text */}
                          <div
                            className="markdown-content text-sm leading-relaxed"
                            style={{ color: "var(--text-primary)" }}
                          >
                            {message.content.split("\n").map((line, i) => (
                              <p key={i} className={line ? "" : "h-2"}>
                                {line}
                              </p>
                            ))}
                          </div>

                          {/* Performance stats */}
                          {message.retrievalMetadata && (
                            <div
                              className="mt-4 pt-3 flex items-center gap-4 text-xs"
                              style={{
                                borderTop: "1px solid var(--border)",
                                color: "var(--text-tertiary)",
                              }}
                            >
                              <span>
                                {(message.retrievalMetadata as Record<string, number>)
                                  .total_time_ms || 0}
                                ms retrieval
                              </span>
                              <span>
                                {(message.generationMetadata as Record<string, number>)
                                  ?.generation_time_ms || 0}
                                ms generation
                              </span>
                              <span>
                                {(message.retrievalMetadata as Record<string, number>)
                                  .final_results || 0}{" "}
                                sources
                              </span>
                            </div>
                          )}
                        </motion.div>

                        {/* Citation chips */}
                        {message.citations && message.citations.length > 0 && (
                          <div className="flex flex-wrap gap-2">
                            {message.citations.map((citation, i) => (
                              <CitationChip
                                key={i}
                                citation={citation}
                                index={i}
                                onClick={() => setSelectedCitation(citation)}
                              />
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input */}
        <div
          className="px-6 py-4"
          style={{ borderTop: "1px solid var(--border)" }}
        >
          <div className="max-w-3xl mx-auto">
            <div
              className="flex items-end gap-3 p-3 rounded-2xl"
              style={{
                background: "var(--surface)",
                border: "1px solid var(--border)",
                boxShadow: "var(--shadow-sm)",
              }}
            >
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about HR policies, benefits, onboarding..."
                className="flex-1 resize-none bg-transparent outline-none text-sm leading-relaxed py-1.5 px-2 max-h-32"
                style={{ color: "var(--text-primary)" }}
                rows={1}
                disabled={isLoading}
              />
              <button
                onClick={() => handleSubmit()}
                disabled={!input.trim() || isLoading}
                className="p-2.5 rounded-xl transition-all flex-shrink-0"
                style={{
                  background:
                    input.trim() && !isLoading
                      ? "var(--accent)"
                      : "var(--surface-tertiary)",
                  color:
                    input.trim() && !isLoading
                      ? "var(--text-inverse)"
                      : "var(--text-tertiary)",
                  cursor:
                    input.trim() && !isLoading ? "pointer" : "not-allowed",
                }}
              >
                <Send size={16} />
              </button>
            </div>
            <p
              className="text-xs text-center mt-2"
              style={{ color: "var(--text-tertiary)" }}
            >
              Answers are grounded in Acme&apos;s approved documents. Always verify
              critical decisions with HR.
            </p>
          </div>
        </div>
      </div>

      {/* ── Source Drawer ── */}
      <SourceDrawer
        citation={selectedCitation}
        onClose={() => setSelectedCitation(null)}
      />
    </div>
  );
}

export default function ChatPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center h-screen" style={{ background: "var(--background)" }}>
        <Loader2 className="animate-spin" size={24} style={{ color: "var(--accent)" }} />
      </div>
    }>
      <ChatPageContent />
    </Suspense>
  );
}
