"use client";

import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import {
  ArrowLeft,
  FileText,
  Users,
  MessageSquare,
  Database,
  CheckCircle2,
  AlertCircle,
  Clock,
  Upload,
  Trash2,
  RefreshCw,
  Sparkles,
  Activity,
  Loader2,
  BarChart3,
  Search,
} from "lucide-react";
import {
  getDashboardStats,
  getDocuments,
  getHealthStatus,
  ingestSampleData,
  deleteDocument,
  uploadDocument,
  syncGoogleDrive,
  type DashboardStats,
  type DocumentInfo,
  type HealthStatus,
} from "@/lib/api";

/* ── Stat Card ── */
function StatCard({
  icon: Icon,
  label,
  value,
  sub,
  accent,
  index,
}: {
  icon: React.ElementType;
  label: string;
  value: string | number;
  sub?: string;
  accent: string;
  index: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08 }}
      className="p-5 rounded-xl"
      style={{
        background: "var(--surface)",
        border: "1px solid var(--border)",
      }}
    >
      <div className="flex items-start justify-between mb-3">
        <div
          className="w-10 h-10 rounded-lg flex items-center justify-center"
          style={{
            background: `color-mix(in srgb, ${accent} 12%, transparent)`,
            color: accent,
          }}
        >
          <Icon size={20} />
        </div>
        {sub && (
          <span className="text-xs" style={{ color: "var(--text-tertiary)" }}>
            {sub}
          </span>
        )}
      </div>
      <p className="text-2xl font-bold" style={{ color: "var(--text-primary)" }}>
        {value}
      </p>
      <p className="text-sm mt-0.5" style={{ color: "var(--text-secondary)" }}>
        {label}
      </p>
    </motion.div>
  );
}

/* ── Status Dot ── */
function StatusDot({ status }: { status: string }) {
  const color =
    status === "ok" || status === "indexed"
      ? "var(--success)"
      : status === "unavailable" || status === "failed"
        ? "var(--error)"
        : "var(--warning)";

  return (
    <span
      className="inline-block w-2 h-2 rounded-full"
      style={{ background: color }}
    />
  );
}

export default function AdminPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [ingesting, setIngesting] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [driveFolderId, setDriveFolderId] = useState("");
  const [activeTab, setActiveTab] = useState<"overview" | "documents" | "health">("overview");

  const fetchData = useCallback(async () => {
    try {
      const [statsData, docsData, healthData] = await Promise.all([
        getDashboardStats().catch(() => null),
        getDocuments().catch(() => []),
        getHealthStatus().catch(() => null),
      ]);
      setStats(statsData);
      setDocuments(docsData);
      setHealth(healthData);
    } catch {
      // Silently handle — will show empty state
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleIngestSample = async () => {
    setIngesting(true);
    try {
      await ingestSampleData();
      await fetchData();
    } catch (error) {
      console.error("Ingestion failed:", error);
    } finally {
      setIngesting(false);
    }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      await uploadDocument(file);
      await fetchData();
    } catch (error) {
      console.error("Upload failed:", error);
    } finally {
      setUploading(false);
    }
  };

  const handleSyncDrive = async () => {
    if (!driveFolderId) return;
    setSyncing(true);
    try {
      await syncGoogleDrive(driveFolderId);
      await fetchData();
      setDriveFolderId("");
    } catch (error) {
      console.error("Drive sync failed:", error);
    } finally {
      setSyncing(false);
    }
  };

  const handleDelete = async (docId: string) => {
    try {
      await deleteDocument(docId);
      await fetchData();
    } catch (error) {
      console.error("Delete failed:", error);
    }
  };

  if (loading) {
    return (
      <div
        className="flex items-center justify-center h-screen"
        style={{ background: "var(--background)" }}
      >
        <Loader2
          className="animate-spin"
          size={24}
          style={{ color: "var(--accent)" }}
        />
      </div>
    );
  }

  return (
    <div
      className="min-h-screen"
      style={{ background: "var(--background)" }}
    >
      {/* Header */}
      <motion.header
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        className="px-6 py-4"
        style={{ borderBottom: "1px solid var(--border)" }}
      >
        <div className="max-w-6xl mx-auto flex items-center justify-between">
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
                <BarChart3 size={16} />
              </div>
              <div>
                <h1
                  className="font-semibold text-sm"
                  style={{ color: "var(--text-primary)" }}
                >
                  Admin Dashboard
                </h1>
                <p
                  className="text-xs"
                  style={{ color: "var(--text-secondary)" }}
                >
                  Document management & analytics
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchData}
              className="p-2 rounded-lg transition-colors"
              style={{ color: "var(--text-secondary)" }}
            >
              <RefreshCw size={16} />
            </button>
            <Link
              href="/chat"
              className="px-4 py-2 rounded-lg text-sm font-medium"
              style={{
                background: "var(--accent)",
                color: "var(--text-inverse)",
              }}
            >
              Open Chat
            </Link>
          </div>
        </div>
      </motion.header>

      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Tabs */}
        <div
          className="flex items-center gap-1 p-1 rounded-xl mb-8 inline-flex"
          style={{ background: "var(--surface-secondary)" }}
        >
          {(
            [
              { id: "overview", label: "Overview", icon: Activity },
              { id: "documents", label: "Documents", icon: FileText },
              { id: "health", label: "System Health", icon: Database },
            ] as const
          ).map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all"
              style={{
                background:
                  activeTab === tab.id ? "var(--surface)" : "transparent",
                color:
                  activeTab === tab.id
                    ? "var(--text-primary)"
                    : "var(--text-secondary)",
                boxShadow:
                  activeTab === tab.id ? "var(--shadow-sm)" : "none",
              }}
            >
              <tab.icon size={14} />
              {tab.label}
            </button>
          ))}
        </div>

        {/* ── Overview Tab ── */}
        {activeTab === "overview" && (
          <div className="space-y-8">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard
                icon={FileText}
                label="Documents Indexed"
                value={stats?.documents.indexed ?? 0}
                sub={`${stats?.documents.total ?? 0} total`}
                accent="var(--info)"
                index={0}
              />
              <StatCard
                icon={Database}
                label="Vector Chunks"
                value={stats?.vector_store.total_chunks ?? 0}
                accent="var(--accent)"
                index={1}
              />
              <StatCard
                icon={MessageSquare}
                label="Total Queries"
                value={stats?.chat.total_queries ?? 0}
                accent="var(--success)"
                index={2}
              />
              <StatCard
                icon={Users}
                label="Active Users"
                value={stats?.users.total ?? 0}
                accent="var(--warning)"
                index={3}
              />
            </div>

            {/* Quick Actions */}
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="p-6 rounded-xl"
              style={{
                background: "var(--surface)",
                border: "1px solid var(--border)",
              }}
            >
              <h3
                className="font-semibold mb-4"
                style={{ color: "var(--text-primary)" }}
              >
                Quick Actions
              </h3>
              <div className="flex flex-wrap gap-3">
                <button
                  onClick={handleIngestSample}
                  disabled={ingesting}
                  className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all"
                  style={{
                    background: "var(--accent)",
                    color: "var(--text-inverse)",
                    opacity: ingesting ? 0.7 : 1,
                  }}
                >
                  {ingesting ? (
                    <Loader2 size={14} className="animate-spin" />
                  ) : (
                    <Sparkles size={14} />
                  )}
                  {ingesting ? "Ingesting..." : "Ingest Sample HR Documents"}
                </button>

                <label
                  className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all cursor-pointer"
                  style={{
                    background: "var(--surface-secondary)",
                    color: "var(--text-primary)",
                    border: "1px solid var(--border)",
                  }}
                >
                  {uploading ? (
                    <Loader2 size={14} className="animate-spin" />
                  ) : (
                    <Upload size={14} />
                  )}
                  Upload Document
                  <input
                    type="file"
                    className="hidden"
                    accept=".pdf,.docx,.txt,.md,.html"
                    onChange={handleUpload}
                    disabled={uploading}
                  />
                </label>
              </div>
            </motion.div>

            {/* Drive Sync Action */}
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.45 }}
              className="p-6 rounded-xl mt-4"
              style={{
                background: "var(--surface)",
                border: "1px solid var(--border)",
              }}
            >
              <h3
                className="font-semibold mb-2"
                style={{ color: "var(--text-primary)" }}
              >
                Google Drive Sync
              </h3>
              <p className="text-sm mb-4" style={{ color: "var(--text-secondary)" }}>
                Sync documents from a shared Google Drive folder directly into the RAG database.
              </p>
              <div className="flex flex-wrap items-center gap-3">
                <input
                  type="text"
                  placeholder="Drive Folder ID"
                  value={driveFolderId}
                  onChange={(e) => setDriveFolderId(e.target.value)}
                  className="px-4 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-1"
                  style={{
                    background: "var(--surface-secondary)",
                    color: "var(--text-primary)",
                    borderColor: "var(--border)",
                  }}
                />
                <button
                  onClick={handleSyncDrive}
                  disabled={syncing || !driveFolderId}
                  className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all"
                  style={{
                    background: "var(--accent)",
                    color: "var(--text-inverse)",
                    opacity: syncing || !driveFolderId ? 0.7 : 1,
                  }}
                >
                  {syncing ? (
                    <Loader2 size={14} className="animate-spin" />
                  ) : (
                    <RefreshCw size={14} />
                  )}
                  {syncing ? "Syncing..." : "Sync Folder"}
                </button>
              </div>
            </motion.div>

            {/* Recent Queries */}
            {stats?.recent_queries && stats.recent_queries.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="p-6 rounded-xl"
                style={{
                  background: "var(--surface)",
                  border: "1px solid var(--border)",
                }}
              >
                <h3
                  className="font-semibold mb-4 flex items-center gap-2"
                  style={{ color: "var(--text-primary)" }}
                >
                  <Search size={16} />
                  Recent Queries
                </h3>
                <div className="space-y-3">
                  {stats.recent_queries.map((q, i) => (
                    <div
                      key={i}
                      className="flex items-center justify-between py-2 px-3 rounded-lg"
                      style={{ background: "var(--surface-secondary)" }}
                    >
                      <span
                        className="text-sm"
                        style={{ color: "var(--text-primary)" }}
                      >
                        {q.query}
                      </span>
                      <div className="flex items-center gap-2">
                        <span
                          className="text-xs px-2 py-0.5 rounded-full"
                          style={{
                            background:
                              q.confidence === "high"
                                ? "var(--success-bg)"
                                : q.confidence === "medium"
                                  ? "var(--warning-bg)"
                                  : "var(--error-bg)",
                            color:
                              q.confidence === "high"
                                ? "var(--success)"
                                : q.confidence === "medium"
                                  ? "var(--warning)"
                                  : "var(--error)",
                          }}
                        >
                          {q.confidence}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </div>
        )}

        {/* ── Documents Tab ── */}
        {activeTab === "documents" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3
                className="font-semibold"
                style={{ color: "var(--text-primary)" }}
              >
                Indexed Documents ({documents.length})
              </h3>
              <div className="flex gap-3">
                <button
                  onClick={handleIngestSample}
                  disabled={ingesting}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium"
                  style={{
                    background: "var(--accent)",
                    color: "var(--text-inverse)",
                  }}
                >
                  {ingesting ? (
                    <Loader2 size={14} className="animate-spin" />
                  ) : (
                    <Sparkles size={14} />
                  )}
                  Ingest Samples
                </button>
              </div>
            </div>

            {documents.length === 0 ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center py-16"
              >
                <FileText
                  size={40}
                  className="mx-auto mb-4"
                  style={{ color: "var(--text-tertiary)" }}
                />
                <p style={{ color: "var(--text-secondary)" }}>
                  No documents indexed yet. Click &ldquo;Ingest Samples&rdquo; to load the
                  HR policy documents.
                </p>
              </motion.div>
            ) : (
              <div className="space-y-3">
                {documents.map((doc, i) => (
                  <motion.div
                    key={doc.id}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className="flex items-center justify-between p-4 rounded-xl"
                    style={{
                      background: "var(--surface)",
                      border: "1px solid var(--border)",
                    }}
                  >
                    <div className="flex items-center gap-4">
                      <div
                        className="w-10 h-10 rounded-lg flex items-center justify-center"
                        style={{
                          background: "var(--accent-lighter)",
                          color: "var(--accent)",
                        }}
                      >
                        <FileText size={18} />
                      </div>
                      <div>
                        <p
                          className="font-medium text-sm"
                          style={{ color: "var(--text-primary)" }}
                        >
                          {doc.title}
                        </p>
                        <p
                          className="text-xs mt-0.5"
                          style={{ color: "var(--text-secondary)" }}
                        >
                          {doc.filename} · {doc.chunk_count} chunks · {doc.department}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-1.5">
                        <StatusDot status={doc.status} />
                        <span
                          className="text-xs capitalize"
                          style={{ color: "var(--text-secondary)" }}
                        >
                          {doc.status}
                        </span>
                      </div>
                      <span
                        className="text-xs px-2 py-0.5 rounded-full"
                        style={{
                          background: "var(--surface-secondary)",
                          color: "var(--text-tertiary)",
                        }}
                      >
                        {doc.permission_level.replace("_", " ")}
                      </span>
                      <button
                        onClick={() => handleDelete(doc.id)}
                        className="p-1.5 rounded-lg transition-colors"
                        style={{ color: "var(--text-tertiary)" }}
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── Health Tab ── */}
        {activeTab === "health" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3
                className="font-semibold"
                style={{ color: "var(--text-primary)" }}
              >
                System Health
              </h3>
              <div
                className="flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium"
                style={{
                  background:
                    health?.status === "healthy"
                      ? "var(--success-bg)"
                      : "var(--warning-bg)",
                  color:
                    health?.status === "healthy"
                      ? "var(--success)"
                      : "var(--warning)",
                }}
              >
                {health?.status === "healthy" ? (
                  <CheckCircle2 size={14} />
                ) : (
                  <AlertCircle size={14} />
                )}
                {health?.status || "unknown"}
              </div>
            </div>

            {health?.services && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {Object.entries(health.services).map(([name, service], i) => (
                  <motion.div
                    key={name}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className="p-5 rounded-xl"
                    style={{
                      background: "var(--surface)",
                      border: "1px solid var(--border)",
                    }}
                  >
                    <div className="flex items-center gap-2 mb-3">
                      <StatusDot status={service.status} />
                      <span
                        className="font-medium text-sm"
                        style={{ color: "var(--text-primary)" }}
                      >
                        {name.replace(/_/g, " ")}
                      </span>
                    </div>
                    <div className="space-y-1 text-xs" style={{ color: "var(--text-secondary)" }}>
                      {Object.entries(service)
                        .filter(([k]) => k !== "status")
                        .map(([k, v]) => (
                          <div key={k} className="flex justify-between">
                            <span>{k.replace(/_/g, " ")}</span>
                            <span style={{ color: "var(--text-primary)" }}>
                              {String(v)}
                            </span>
                          </div>
                        ))}
                    </div>
                  </motion.div>
                ))}
              </div>
            )}

            {!health && (
              <div className="text-center py-12">
                <AlertCircle
                  size={40}
                  className="mx-auto mb-4"
                  style={{ color: "var(--error)" }}
                />
                <p style={{ color: "var(--text-secondary)" }}>
                  Cannot connect to the backend. Make sure the FastAPI server is
                  running on port 8000.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
