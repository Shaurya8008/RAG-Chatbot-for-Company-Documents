"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import {
  Search,
  FileText,
  Shield,
  Zap,
  ArrowRight,
  BookOpen,
  Clock,
  CheckCircle2,
  Sparkles,
} from "lucide-react";

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] },
  }),
};

const stagger = {
  visible: {
    transition: { staggerChildren: 0.08 },
  },
};

export default function HomePage() {
  return (
    <div
      className="min-h-screen"
      style={{ background: "var(--background)", color: "var(--foreground)" }}
    >
      {/* ── Navigation ── */}
      <motion.nav
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="fixed top-0 left-0 right-0 z-50 px-6 py-4"
        style={{
          background: "color-mix(in srgb, var(--background) 80%, transparent)",
          backdropFilter: "blur(12px)",
          borderBottom: "1px solid var(--border)",
        }}
      >
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center"
              style={{ background: "var(--accent)", color: "var(--text-inverse)" }}
            >
              <Sparkles size={18} />
            </div>
            <span className="font-semibold text-lg tracking-tight">
              Acme Knowledge
            </span>
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/admin"
              className="px-4 py-2 text-sm rounded-lg transition-colors"
              style={{ color: "var(--text-secondary)" }}
              onMouseEnter={(e) =>
                (e.currentTarget.style.color = "var(--text-primary)")
              }
              onMouseLeave={(e) =>
                (e.currentTarget.style.color = "var(--text-secondary)")
              }
            >
              Admin
            </Link>
            <Link
              href="/chat"
              className="px-5 py-2.5 text-sm font-medium rounded-lg transition-all"
              style={{
                background: "var(--accent)",
                color: "var(--text-inverse)",
              }}
            >
              Open Assistant
            </Link>
          </div>
        </div>
      </motion.nav>

      {/* ── Hero ── */}
      <section className="pt-36 pb-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium mb-8"
            style={{
              background: "var(--accent-lighter)",
              color: "var(--accent-dark)",
              border: "1px solid var(--accent-light)",
            }}
          >
            <Shield size={14} />
            Internal Knowledge Assistant
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-5xl md:text-6xl font-bold tracking-tight leading-tight mb-6"
          >
            Find answers across
            <br />
            <span style={{ color: "var(--accent)" }}>company knowledge</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-lg md:text-xl max-w-2xl mx-auto mb-10 leading-relaxed"
            style={{ color: "var(--text-secondary)" }}
          >
            Ask questions about HR policies, onboarding, benefits, and company
            procedures. Get instant, cited answers grounded in approved documents.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Link
              href="/chat"
              className="group flex items-center gap-2 px-8 py-4 text-base font-semibold rounded-xl transition-all"
              style={{
                background: "var(--accent)",
                color: "var(--text-inverse)",
                boxShadow: "var(--shadow-md)",
              }}
            >
              Start asking
              <ArrowRight
                size={18}
                className="transition-transform group-hover:translate-x-1"
              />
            </Link>
            <Link
              href="/admin"
              className="flex items-center gap-2 px-8 py-4 text-base font-medium rounded-xl transition-all"
              style={{
                background: "var(--surface)",
                color: "var(--text-primary)",
                border: "1px solid var(--border)",
              }}
            >
              <FileText size={18} />
              View Documents
            </Link>
          </motion.div>
        </div>
      </section>

      {/* ── Feature Cards ── */}
      <section className="py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <motion.div
            variants={stagger}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            className="grid grid-cols-1 md:grid-cols-3 gap-6"
          >
            {[
              {
                icon: Search,
                title: "Hybrid Retrieval",
                desc: "Combines semantic search with keyword matching and cross-encoder reranking for precise, reliable results.",
                accent: "var(--info)",
              },
              {
                icon: Shield,
                title: "Permission-Aware",
                desc: "Role-based access control ensures you only see documents you're authorized to access. Enforced before generation.",
                accent: "var(--success)",
              },
              {
                icon: Zap,
                title: "Cited Answers",
                desc: "Every response is grounded in source documents with clickable citations. No hallucinations — verify every claim.",
                accent: "var(--accent)",
              },
            ].map((feature, i) => (
              <motion.div
                key={feature.title}
                custom={i}
                variants={fadeUp}
                className="p-7 rounded-2xl transition-all cursor-default"
                style={{
                  background: "var(--surface)",
                  border: "1px solid var(--border)",
                  boxShadow: "var(--shadow-sm)",
                }}
                whileHover={{
                  y: -4,
                  boxShadow: "var(--shadow-lg)",
                  transition: { duration: 0.2 },
                }}
              >
                <div
                  className="w-11 h-11 rounded-xl flex items-center justify-center mb-5"
                  style={{
                    background: `color-mix(in srgb, ${feature.accent} 12%, transparent)`,
                    color: feature.accent,
                  }}
                >
                  <feature.icon size={22} />
                </div>
                <h3
                  className="text-lg font-semibold mb-2"
                  style={{ color: "var(--text-primary)" }}
                >
                  {feature.title}
                </h3>
                <p
                  className="text-sm leading-relaxed"
                  style={{ color: "var(--text-secondary)" }}
                >
                  {feature.desc}
                </p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ── Example Queries ── */}
      <section className="py-20 px-6" style={{ background: "var(--surface-secondary)" }}>
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl font-bold mb-3">Try asking</h2>
            <p style={{ color: "var(--text-secondary)" }}>
              Example questions from the HR policy library
            </p>
          </motion.div>

          <motion.div
            variants={stagger}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-50px" }}
            className="grid grid-cols-1 md:grid-cols-2 gap-4"
          >
            {[
              {
                q: "How many PTO days do I get in my first year?",
                icon: Clock,
              },
              {
                q: "What is the 401(k) matching policy?",
                icon: BookOpen,
              },
              {
                q: "What happens during my 90-day probation period?",
                icon: CheckCircle2,
              },
              {
                q: "How do I report a workplace concern?",
                icon: Shield,
              },
            ].map((example, i) => (
              <motion.div key={i} custom={i} variants={fadeUp}>
                <Link
                  href={`/chat?q=${encodeURIComponent(example.q)}`}
                  className="group flex items-start gap-4 p-5 rounded-xl transition-all"
                  style={{
                    background: "var(--surface)",
                    border: "1px solid var(--border)",
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = "var(--accent)";
                    e.currentTarget.style.boxShadow = "var(--shadow-md)";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = "var(--border)";
                    e.currentTarget.style.boxShadow = "none";
                  }}
                >
                  <div
                    className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                    style={{
                      background: "var(--accent-lighter)",
                      color: "var(--accent)",
                    }}
                  >
                    <example.icon size={18} />
                  </div>
                  <div className="flex-1">
                    <p
                      className="font-medium text-sm leading-snug"
                      style={{ color: "var(--text-primary)" }}
                    >
                      {example.q}
                    </p>
                  </div>
                  <ArrowRight
                    size={16}
                    className="flex-shrink-0 mt-1 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all"
                    style={{ color: "var(--accent)" }}
                  />
                </Link>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer
        className="py-8 px-6 text-center text-sm"
        style={{
          color: "var(--text-tertiary)",
          borderTop: "1px solid var(--border)",
        }}
      >
        <p>
          Acme Knowledge Assistant — Internal use only · Powered by RAG with
          local AI
        </p>
      </footer>
    </div>
  );
}
