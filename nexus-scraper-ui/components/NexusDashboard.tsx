"use client";

import React, { useState, useRef, useCallback, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Search, Download, AlertTriangle, Loader2,
    Database, Table2, Globe, Zap, Clock,
    ArrowRight, Trash2, ExternalLink, Key, Eye, EyeOff, Settings
} from "lucide-react";

// ── Types ────────────────────────────────────────────────────────────────────
interface FieldSchema { type: string; description: string; }
interface CategorySchema { fields: Record<string, FieldSchema>; }
interface ScrapeResponse {
    status: string;
    schema: Record<string, CategorySchema>;
    data: Record<string, Record<string, any>[]>;
    entityCount: number;
    totalItems: number;
    timestamp: string;
    url: string;
}
interface HistoryEntry {
    id: string;
    url: string;
    timestamp: string;
    entityCount: number;
    totalItems: number;
    result: ScrapeResponse;
}

const HISTORY_KEY = "aria_history";
const MAX_HISTORY = 5;

// ── Feature SVG Illustrations ────────────────────────────────────────────────
function UniversalIllustration() {
    return (
        <svg viewBox="0 0 80 80" fill="none" className="w-16 h-16">
            <circle cx="40" cy="40" r="28" stroke="url(#g1)" strokeWidth="1.5" strokeDasharray="4 3" />
            <circle cx="40" cy="40" r="18" stroke="url(#g1)" strokeWidth="1.5" opacity="0.6" />
            <ellipse cx="40" cy="40" rx="28" ry="12" stroke="url(#g1)" strokeWidth="1" opacity="0.4" />
            <circle cx="40" cy="12" r="3" fill="#34d399" />
            <circle cx="62" cy="52" r="2.5" fill="#22d3ee" />
            <circle cx="18" cy="48" r="2" fill="#a78bfa" />
            <line x1="40" y1="15" x2="40" y2="40" stroke="#34d399" strokeWidth="0.8" opacity="0.4" />
            <line x1="40" y1="40" x2="60" y2="51" stroke="#22d3ee" strokeWidth="0.8" opacity="0.4" />
            <line x1="40" y1="40" x2="20" y2="47" stroke="#a78bfa" strokeWidth="0.8" opacity="0.4" />
            <circle cx="40" cy="40" r="4" fill="url(#g1)" />
            <defs><linearGradient id="g1" x1="12" y1="12" x2="68" y2="68"><stop stopColor="#34d399" /><stop offset="1" stopColor="#22d3ee" /></linearGradient></defs>
        </svg>
    );
}

function AIIllustration() {
    return (
        <svg viewBox="0 0 80 80" fill="none" className="w-16 h-16">
            {/* Neural network nodes */}
            {[[20, 22], [20, 40], [20, 58], [40, 28], [40, 52], [60, 32], [60, 48], [40, 40]].map(([cx, cy], i) => (
                <circle key={i} cx={cx} cy={cy} r={i === 7 ? 5 : 3} fill={i === 7 ? "url(#g2)" : "none"} stroke="url(#g2)" strokeWidth={i === 7 ? 0 : 1.2} opacity={i < 3 ? 0.5 : 0.8} />
            ))}
            {/* Connections */}
            {[[20, 22, 40, 28], [20, 22, 40, 40], [20, 40, 40, 28], [20, 40, 40, 52], [20, 40, 40, 40], [20, 58, 40, 52], [20, 58, 40, 40], [40, 28, 60, 32], [40, 28, 60, 48], [40, 40, 60, 32], [40, 40, 60, 48], [40, 52, 60, 32], [40, 52, 60, 48]].map(([x1, y1, x2, y2], i) => (
                <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="url(#g2)" strokeWidth="0.6" opacity="0.25" />
            ))}
            {/* Pulse rings */}
            <circle cx="40" cy="40" r="12" stroke="#a78bfa" strokeWidth="0.8" opacity="0.2" strokeDasharray="2 3" />
            <circle cx="40" cy="40" r="22" stroke="#a78bfa" strokeWidth="0.5" opacity="0.1" strokeDasharray="3 4" />
            <defs><linearGradient id="g2" x1="20" y1="20" x2="60" y2="60"><stop stopColor="#a78bfa" /><stop offset="1" stopColor="#c084fc" /></linearGradient></defs>
        </svg>
    );
}

function StealthIllustration() {
    return (
        <svg viewBox="0 0 80 80" fill="none" className="w-16 h-16">
            <rect x="18" y="24" width="44" height="32" rx="4" stroke="url(#g3)" strokeWidth="1.5" />
            <rect x="22" y="28" width="36" height="22" rx="2" stroke="url(#g3)" strokeWidth="0.8" opacity="0.3" />
            {/* Shield */}
            <path d="M40 34 L48 38 L48 46 C48 50 44 53 40 55 C36 53 32 50 32 46 L32 38 Z" stroke="url(#g3)" strokeWidth="1.5" fill="none" />
            <path d="M37 44 L39.5 46.5 L44 41" stroke="#f59e0b" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            {/* Signal waves */}
            <path d="M54 30 C57 30 58 32 58 35" stroke="#f59e0b" strokeWidth="0.8" opacity="0.4" strokeLinecap="round" />
            <path d="M54 28 C59 28 61 32 61 37" stroke="#f59e0b" strokeWidth="0.6" opacity="0.25" strokeLinecap="round" />
            <defs><linearGradient id="g3" x1="18" y1="24" x2="62" y2="56"><stop stopColor="#f59e0b" /><stop offset="1" stopColor="#f97316" /></linearGradient></defs>
        </svg>
    );
}

function StructuredIllustration() {
    return (
        <svg viewBox="0 0 80 80" fill="none" className="w-16 h-16">
            {/* JSON brackets */}
            <path d="M24 25 L18 25 C16 25 15 26 15 28 L15 37 C15 39 14 40 12 40 C14 40 15 41 15 43 L15 52 C15 54 16 55 18 55 L24 55" stroke="url(#g4)" strokeWidth="1.5" strokeLinecap="round" />
            <path d="M56 25 L62 25 C64 25 65 26 65 28 L65 37 C65 39 66 40 68 40 C66 40 65 41 65 43 L65 52 C65 54 64 55 62 55 L56 55" stroke="url(#g4)" strokeWidth="1.5" strokeLinecap="round" />
            {/* Data rows */}
            <rect x="28" y="32" width="24" height="4" rx="1" fill="#06b6d4" opacity="0.3" />
            <rect x="28" y="39" width="18" height="4" rx="1" fill="#06b6d4" opacity="0.2" />
            <rect x="28" y="46" width="21" height="4" rx="1" fill="#06b6d4" opacity="0.15" />
            {/* Key dots */}
            <circle cx="30" cy="34" r="1.5" fill="#22d3ee" />
            <circle cx="30" cy="41" r="1.5" fill="#22d3ee" opacity="0.7" />
            <circle cx="30" cy="48" r="1.5" fill="#22d3ee" opacity="0.5" />
            <defs><linearGradient id="g4" x1="12" y1="25" x2="68" y2="55"><stop stopColor="#06b6d4" /><stop offset="1" stopColor="#3b82f6" /></linearGradient></defs>
        </svg>
    );
}

const FEATURES = [
    { Illustration: UniversalIllustration, title: "Universal Extraction", desc: "Works on any webpage — e-commerce, news, social media, music platforms, dashboards, forums, wikis, and more. No hardcoded selectors needed." },
    { Illustration: AIIllustration, title: "Gemini 2.5 AI Engine", desc: "Google's latest AI model reads the page semantically, discovers the data schema, and structures everything automatically." },
    { Illustration: StealthIllustration, title: "Stealth Browser", desc: "DrissionPage with fingerprint randomization, anti-detection scripts, and human-like scrolling behavior. Bypasses most protections." },
    { Illustration: StructuredIllustration, title: "Schema-Perfect JSON", desc: "Every column aligned, every field typed. Null-safe output with instant CSV and JSON export. Ready for analysis." },
];

// ── Main Component ───────────────────────────────────────────────────────────
export default function NexusDashboard() {
    const [url, setUrl] = useState("");
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<ScrapeResponse | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [logs, setLogs] = useState<string[]>([]);
    const [elapsed, setElapsed] = useState(0);
    const [history, setHistory] = useState<HistoryEntry[]>([]);
    const [geminiKey, setGeminiKey] = useState("");
    const [showKey, setShowKey] = useState(false);
    const [showSettings, setShowSettings] = useState(false);
    const timerRef = useRef<NodeJS.Timeout | null>(null);

    // Load history + API key on mount
    useEffect(() => {
        try {
            const saved = localStorage.getItem(HISTORY_KEY);
            if (saved) setHistory(JSON.parse(saved));
            const savedKey = localStorage.getItem("aria_gemini_key");
            if (savedKey) setGeminiKey(savedKey);
        } catch { }
    }, []);

    const saveHistory = (entries: HistoryEntry[]) => {
        setHistory(entries);
        localStorage.setItem(HISTORY_KEY, JSON.stringify(entries));
    };

    const addLog = useCallback((msg: string) => {
        setLogs((prev) => [...prev.slice(-5), msg]);
    }, []);

    const handleScrape = async () => {
        if (!url.trim()) return;

        // ── Security: URL Validation ─────────────────────────────
        const trimmed = url.trim();
        try {
            const parsed = new URL(trimmed);
            if (!["http:", "https:"].includes(parsed.protocol)) {
                setError("Only http:// and https:// URLs are allowed.");
                return;
            }
            // Block internal/private addresses (SSRF protection)
            const host = parsed.hostname.toLowerCase();
            if (host === "localhost" || host === "127.0.0.1" || host === "0.0.0.0" ||
                host.startsWith("192.168.") || host.startsWith("10.") || host.startsWith("172.") ||
                host.endsWith(".local") || host.endsWith(".internal")) {
                setError("Internal/private network URLs are not allowed for security reasons.");
                return;
            }
        } catch {
            setError("Please enter a valid URL (e.g. https://example.com)");
            return;
        }

        setLoading(true);
        setResult(null);
        setError(null);
        setElapsed(0);
        setLogs(["Initializing browser agent...", "Opening secure tunnel..."]);

        timerRef.current = setInterval(() => setElapsed((p) => p + 0.1), 100);

        try {
            addLog("Navigating to target page...");

            const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
            const res = await fetch(`${API_URL}/api/scrape`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    url: url.trim(),
                    config: { stealthMode: true, headlessMode: false, geminiParsing: true },
                    geminiKey: geminiKey || undefined,
                }),
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
                throw new Error(errData.detail || `Server error: ${res.status}`);
            }

            const json: ScrapeResponse = await res.json();
            if (timerRef.current) clearInterval(timerRef.current);
            setLoading(false);
            setResult(json);

            // Save to history (FIFO: max 5)
            const entry: HistoryEntry = {
                id: Date.now().toString(),
                url: url.trim(),
                timestamp: new Date().toLocaleString(),
                entityCount: json.entityCount,
                totalItems: json.totalItems,
                result: json,
            };
            const updated = [...history, entry].slice(-MAX_HISTORY);
            saveHistory(updated);

            if (json.totalItems === 0) {
                addLog("Page returned minimal data.");
            } else {
                addLog(`Done — ${json.entityCount} categories, ${json.totalItems} items`);
            }
        } catch (e: any) {
            if (timerRef.current) clearInterval(timerRef.current);
            setLoading(false);
            setError(e.message || "Connection failed");
            addLog(`Error: ${e.message}`);
        }
    };

    const loadFromHistory = (entry: HistoryEntry) => {
        setUrl(entry.url);
        setResult(entry.result);
        setError(null);
        setLogs([`Loaded from history: ${entry.url}`]);
    };

    const deleteHistory = (id: string) => {
        const updated = history.filter((h) => h.id !== id);
        saveHistory(updated);
    };

    const clearHistory = () => saveHistory([]);

    const exportJSON = () => {
        if (!result) return;
        const blob = new Blob([JSON.stringify(result.data, null, 2)], { type: "application/json" });
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = `aria-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(a.href);
    };

    const exportCSV = (category: string, items: Record<string, any>[]) => {
        if (!result || !items.length) return;
        const fields = result.schema[category]
            ? Object.keys(result.schema[category].fields) : Object.keys(items[0]);
        const header = fields.join(",");
        const rows = items.map((item) =>
            fields.map((f) => {
                const v = item[f];
                if (v === null || v === undefined) return "";
                return `"${String(v).replace(/"/g, '""')}"`;
            }).join(",")
        );
        const blob = new Blob([[header, ...rows].join("\n")], { type: "text/csv" });
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = `${category}-${Date.now()}.csv`;
        a.click();
        URL.revokeObjectURL(a.href);
    };

    return (
        <div className="min-h-screen relative">
            {/* Floating orbs */}
            <div className="orb" style={{ width: 400, height: 400, top: -100, left: -100, background: "rgba(16, 185, 129, 0.5)" }} />
            <div className="orb" style={{ width: 350, height: 350, bottom: -50, right: -50, background: "rgba(6, 182, 212, 0.4)", animationDelay: "-5s" }} />
            <div className="orb" style={{ width: 250, height: 250, top: "40%", right: "20%", background: "rgba(139, 92, 246, 0.3)", animationDelay: "-10s" }} />

            <div className="relative z-10 max-w-6xl mx-auto px-6 py-10">

                {/* ── HERO ──────────────────────────────────────────── */}
                <motion.div initial={{ opacity: 0, y: -30 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-8">
                    <h1 className="text-7xl md:text-8xl font-extrabold tracking-tight leading-none mb-4">
                        <span className="text-transparent bg-clip-text bg-gradient-to-br from-emerald-300 via-teal-200 to-cyan-300">
                            Aria
                        </span>
                    </h1>
                    <p className="text-gray-500 text-lg max-w-lg mx-auto leading-relaxed font-light">
                        Paste any URL. Aria reads the page, understands it,
                        and returns perfectly structured data.
                    </p>
                </motion.div>

                {/* ── FEATURE CARDS (2×2) ──────────────────────────── */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.1 }}
                    className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-10"
                >
                    {FEATURES.map((f, i) => (
                        <motion.div
                            key={f.title}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.15 + i * 0.06 }}
                            className="glass-card glass-card-hover rounded-2xl p-5 flex flex-col items-center text-center cursor-default group"
                        >
                            <div className="mb-3 opacity-70 group-hover:opacity-100 transition-opacity duration-300">
                                <f.Illustration />
                            </div>
                            <h3 className="text-white text-sm font-bold mb-1.5">{f.title}</h3>
                            <p className="text-gray-500 text-xs leading-relaxed">{f.desc}</p>
                        </motion.div>
                    ))}
                </motion.div>

                {/* ── MAIN INPUT CARD ──────────────────────────────── */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.25 }}
                    className="glass-card gradient-border rounded-2xl overflow-hidden glow-emerald"
                >
                    <div className="p-6 md:p-8 space-y-5">
                        {/* API Key Settings */}
                        <div>
                            <button
                                onClick={() => setShowSettings(!showSettings)}
                                className="flex items-center space-x-2 text-xs text-gray-500 hover:text-gray-300 transition-colors mb-3"
                            >
                                <Settings size={13} className={showSettings ? "text-emerald-400" : ""} />
                                <span>API Key</span>
                                {geminiKey ? (
                                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 ml-1" />
                                ) : (
                                    <span className="text-red-400 text-[10px] ml-1">required</span>
                                )}
                            </button>
                            <AnimatePresence>
                                {showSettings && (
                                    <motion.div
                                        initial={{ height: 0, opacity: 0 }}
                                        animate={{ height: "auto", opacity: 1 }}
                                        exit={{ height: 0, opacity: 0 }}
                                        className="overflow-hidden"
                                    >
                                        <div className="bg-white/[0.02] border border-white/[0.06] rounded-xl p-4 mb-4 space-y-3">
                                            <div className="flex items-center space-x-2">
                                                <Key size={14} className="text-emerald-500 flex-shrink-0" />
                                                <p className="text-gray-400 text-xs">
                                                    Enter your Gemini API key.{" "}
                                                    <a
                                                        href="https://aistudio.google.com/apikey"
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="text-emerald-500/70 hover:text-emerald-400 underline transition-colors"
                                                    >
                                                        Get a free key →
                                                    </a>
                                                </p>
                                            </div>
                                            <div className="relative">
                                                <input
                                                    type={showKey ? "text" : "password"}
                                                    value={geminiKey}
                                                    onChange={(e) => {
                                                        setGeminiKey(e.target.value);
                                                        localStorage.setItem("aria_gemini_key", e.target.value);
                                                    }}
                                                    placeholder="AIza..."
                                                    className="w-full bg-white/[0.03] border border-white/[0.08] rounded-lg py-2.5 pl-3 pr-10 text-white font-mono text-xs focus:outline-none focus:border-emerald-500/30 transition-all placeholder:text-gray-700"
                                                />
                                                <button
                                                    onClick={() => setShowKey(!showKey)}
                                                    className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-600 hover:text-gray-400 transition-colors"
                                                >
                                                    {showKey ? <EyeOff size={14} /> : <Eye size={14} />}
                                                </button>
                                            </div>
                                            <p className="text-gray-600 text-[10px]">
                                                🔒 Stored locally in your browser. Never sent to third parties.
                                            </p>
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>

                        {/* URL Input */}
                        <div className="relative group">
                            <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                                <Search className="h-5 w-5 text-gray-600 group-focus-within:text-emerald-400 transition-colors duration-300" />
                            </div>
                            <input
                                type="text"
                                value={url}
                                onChange={(e) => setUrl(e.target.value)}
                                onKeyDown={(e) => e.key === "Enter" && !loading && handleScrape()}
                                placeholder="https://example.com"
                                className="w-full bg-white/[0.03] border border-white/[0.08] rounded-xl py-4 pl-12 pr-44 text-white font-mono text-sm focus:outline-none focus:border-emerald-500/30 focus:bg-white/[0.05] transition-all duration-300 placeholder:text-gray-700"
                            />
                            <button
                                onClick={handleScrape}
                                disabled={loading || !url.trim()}
                                className="absolute right-2 top-2 bottom-2 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 disabled:from-gray-700 disabled:to-gray-700 disabled:opacity-40 text-white px-6 rounded-lg font-semibold text-sm tracking-wide transition-all duration-200 flex items-center space-x-2 shadow-lg shadow-emerald-950/30"
                            >
                                {loading ? <Loader2 size={15} className="animate-spin" /> : <ArrowRight size={15} />}
                                <span>{loading ? "Extracting" : "Extract"}</span>
                            </button>
                        </div>

                        {/* Terminal */}
                        <div className="relative bg-[#08080d] rounded-xl border border-white/[0.04] overflow-hidden">
                            <div className="h-8 border-b border-white/[0.04] flex items-center px-3 space-x-1.5">
                                <div className="w-2.5 h-2.5 rounded-full bg-[#ff5f57]" />
                                <div className="w-2.5 h-2.5 rounded-full bg-[#febc2e]" />
                                <div className="w-2.5 h-2.5 rounded-full bg-[#28c840]" />
                                <span className="ml-3 text-[10px] text-gray-600 font-mono">aria_agent</span>
                            </div>
                            <div className="p-4 h-28 font-mono text-xs text-gray-500 overflow-hidden">
                                {logs.map((log, i) => (
                                    <motion.div key={`${i}-${log}`} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} className="mb-1 flex items-start">
                                        <span className="text-emerald-600 mr-2 flex-shrink-0">$</span>
                                        <span className="text-gray-400">{log}</span>
                                    </motion.div>
                                ))}
                            </div>
                            {loading && (
                                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="absolute bottom-3 right-4 flex items-baseline space-x-1">
                                    <span className="text-3xl font-bold tabular-nums text-emerald-400 drop-shadow-[0_0_8px_rgba(16,185,129,0.4)]">
                                        {elapsed.toFixed(1)}
                                    </span>
                                    <span className="text-emerald-600 text-xs font-medium">sec</span>
                                </motion.div>
                            )}
                        </div>
                    </div>
                </motion.div>

                {/* ── ERROR ────────────────────────────────────────── */}
                <AnimatePresence>
                    {error && (
                        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}
                            className="mt-6 p-4 bg-red-500/5 border border-red-500/15 rounded-xl flex items-start space-x-3">
                            <AlertTriangle className="text-red-400 flex-shrink-0 mt-0.5" size={18} />
                            <div>
                                <p className="text-red-400 font-semibold text-sm">Extraction Failed</p>
                                <p className="text-red-400/60 text-xs mt-1">{error}</p>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* ── LOADING ──────────────────────────────────────── */}
                {loading && (
                    <div className="mt-8 space-y-4">
                        <div className="flex items-center justify-center space-x-2 text-gray-500 text-sm">
                            <Zap size={14} className="text-emerald-500 animate-pulse" />
                            <span>Aria is reading and organizing data...</span>
                        </div>
                        {[1, 2].map((i) => (
                            <div key={i} className="glass-card rounded-xl p-6 space-y-3 animate-pulse">
                                <div className="h-3 bg-white/[0.04] rounded w-1/4" />
                                <div className="h-2.5 bg-white/[0.03] rounded w-full" />
                                <div className="h-2.5 bg-white/[0.03] rounded w-4/5" />
                            </div>
                        ))}
                    </div>
                )}

                {/* ── RESULTS ──────────────────────────────────────── */}
                <div className="mt-8 space-y-6">
                    <AnimatePresence>
                        {result && (
                            <>
                                {/* Summary */}
                                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                                    className="glass-card rounded-xl px-6 py-4 flex flex-wrap items-center justify-between gap-3">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center">
                                            <Database size={16} className="text-white" />
                                        </div>
                                        <div>
                                            <p className="text-white font-semibold text-sm">Extraction Complete</p>
                                            <p className="text-gray-500 text-xs">{result.entityCount} categories · {result.totalItems} items · {elapsed.toFixed(1)}s</p>
                                        </div>
                                    </div>
                                    <button onClick={exportJSON}
                                        className="flex items-center space-x-2 text-xs bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-gray-300 hover:text-white px-4 py-2 rounded-lg transition-all font-medium">
                                        <Download size={13} /><span>Export JSON</span>
                                    </button>
                                </motion.div>

                                {/* Category Tables */}
                                {Object.entries(result.data).map(([category, items], idx) => {
                                    const schemaFields = result.schema[category]?.fields;
                                    const columns: string[] = schemaFields
                                        ? Object.keys(schemaFields)
                                        : (Array.isArray(items) && items.length > 0 && typeof items[0] === "object" ? Object.keys(items[0]) : []);

                                    return (
                                        <motion.div key={category} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.05 }}>
                                            <div className="flex items-center justify-between mb-3">
                                                <div className="flex items-center space-x-2.5">
                                                    <Table2 className="text-emerald-500" size={15} />
                                                    <h2 className="text-sm font-bold text-white tracking-wide">{category.replace(/([A-Z])/g, " $1").trim()}</h2>
                                                    <span className="text-[10px] bg-white/[0.06] px-2 py-0.5 rounded-full text-gray-500 font-medium">
                                                        {Array.isArray(items) ? items.length : 1}
                                                    </span>
                                                </div>
                                                {Array.isArray(items) && items.length > 0 && (
                                                    <button onClick={() => exportCSV(category, items)}
                                                        className="text-[11px] text-gray-500 hover:text-gray-300 bg-white/[0.03] hover:bg-white/[0.06] px-3 py-1.5 rounded-lg border border-white/[0.05] transition-all font-medium">
                                                        CSV ↓
                                                    </button>
                                                )}
                                            </div>
                                            <div className="glass-card rounded-xl overflow-hidden">
                                                <div className="overflow-x-auto">
                                                    <table className="nexus-table w-full text-left">
                                                        <thead>
                                                            <tr>
                                                                <th className="w-10 text-center">#</th>
                                                                {columns.map((col) => <th key={col}>{col.replace(/([A-Z])/g, " $1").trim()}</th>)}
                                                            </tr>
                                                        </thead>
                                                        <tbody>
                                                            {Array.isArray(items) ? items.map((row, rIdx) => (
                                                                <tr key={rIdx}>
                                                                    <td className="text-center text-gray-700 text-xs">{rIdx + 1}</td>
                                                                    {columns.map((col) => <td key={col}>{renderCell(row?.[col], schemaFields?.[col]?.type)}</td>)}
                                                                </tr>
                                                            )) : (
                                                                <tr><td colSpan={columns.length + 1}><pre className="text-xs text-gray-500 p-3 whitespace-pre-wrap">{JSON.stringify(items, null, 2)}</pre></td></tr>
                                                            )}
                                                        </tbody>
                                                    </table>
                                                </div>
                                            </div>
                                        </motion.div>
                                    );
                                })}
                            </>
                        )}
                    </AnimatePresence>
                </div>

                {/* ── HISTORY PANEL ────────────────────────────────── */}
                {history.length > 0 && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="mt-12 mb-8"
                    >
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center space-x-2">
                                <Clock size={16} className="text-gray-500" />
                                <h2 className="text-sm font-bold text-white tracking-wide">Recent Extractions</h2>
                                <span className="text-[10px] bg-white/[0.06] px-2 py-0.5 rounded-full text-gray-500 font-medium">{history.length}/{MAX_HISTORY}</span>
                            </div>
                            <button onClick={clearHistory} className="text-[11px] text-gray-600 hover:text-red-400 transition-colors">
                                Clear all
                            </button>
                        </div>
                        <div className="space-y-2">
                            {[...history].reverse().map((entry) => (
                                <motion.div
                                    key={entry.id}
                                    layout
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: 10 }}
                                    className="glass-card glass-card-hover rounded-xl px-5 py-3.5 flex items-center justify-between group cursor-pointer"
                                    onClick={() => loadFromHistory(entry)}
                                >
                                    <div className="flex items-center space-x-3 min-w-0 flex-1">
                                        <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/15 flex items-center justify-center flex-shrink-0">
                                            <Globe size={14} className="text-emerald-500" />
                                        </div>
                                        <div className="min-w-0 flex-1">
                                            <p className="text-white text-sm font-medium truncate">{entry.url}</p>
                                            <p className="text-gray-600 text-xs">
                                                {entry.timestamp} · {entry.entityCount} categories · {entry.totalItems} items
                                            </p>
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-1 ml-3">
                                        <button className="p-1.5 rounded-lg hover:bg-white/[0.06] text-gray-600 hover:text-emerald-400 transition-all opacity-0 group-hover:opacity-100"
                                            onClick={(e) => { e.stopPropagation(); loadFromHistory(entry); }} title="Load result">
                                            <ExternalLink size={13} />
                                        </button>
                                        <button className="p-1.5 rounded-lg hover:bg-red-500/10 text-gray-600 hover:text-red-400 transition-all opacity-0 group-hover:opacity-100"
                                            onClick={(e) => { e.stopPropagation(); deleteHistory(entry.id); }} title="Delete">
                                            <Trash2 size={13} />
                                        </button>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </motion.div>
                )}

                {/* ── EMPTY STATE ──────────────────────────────────── */}
                {!result && !loading && !error && history.length === 0 && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }} className="text-center py-16">
                        <div className="relative w-20 h-20 mx-auto mb-6">
                            <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 blur-xl" />
                            <div className="relative w-20 h-20 rounded-2xl bg-gradient-to-br from-emerald-500/10 to-cyan-500/10 border border-white/[0.06] flex items-center justify-center">
                                <Globe size={32} className="text-emerald-500/40" />
                            </div>
                        </div>
                        <h3 className="text-gray-300 text-xl font-semibold mb-2">Ready when you are</h3>
                        <p className="text-gray-600 text-sm max-w-md mx-auto leading-relaxed">
                            Paste any URL above — Aria will visit the page, understand its content,
                            and return clean, structured data you can export instantly.
                        </p>
                        <div className="flex flex-wrap justify-center gap-2 mt-8">
                            {["E-commerce", "News", "Social Media", "Music", "Real Estate", "Any page"].map((t) => (
                                <span key={t} className="text-xs bg-white/[0.03] border border-white/[0.05] text-gray-500 px-3 py-1.5 rounded-lg">{t}</span>
                            ))}
                        </div>
                    </motion.div>
                )}

                {/* ── FOOTER ──────────────────────────────────────── */}
                <div className="mt-16 pb-8 text-center">
                    <p className="text-gray-700 text-xs">
                        Built with DrissionPage + Google Gemini AI ·{" "}
                        <a href="/privacy" className="hover:text-gray-500 transition-colors">Privacy</a>{" · "}
                        <a href="/terms" className="hover:text-gray-500 transition-colors">Terms</a>
                    </p>
                </div>
            </div>
        </div>
    );
}

// ── Cell Renderer ────────────────────────────────────────────────────────────
function renderCell(val: any, type?: string): React.ReactNode {
    if (val === null || val === undefined) return <span className="text-gray-700">—</span>;
    const str = String(val);
    if (type === "url" || str.startsWith("http://") || str.startsWith("https://")) {
        return <a href={str} target="_blank" rel="noopener noreferrer" className="text-cyan-400/80 hover:text-cyan-300 transition-colors" title={str}>{str.length > 40 ? str.slice(0, 37) + "…" : str}</a>;
    }
    if (type === "number" || (typeof val === "number" && !isNaN(val))) return <span className="tabular-nums text-gray-300">{val}</span>;
    if (type === "boolean" || typeof val === "boolean") return val ? <span className="text-emerald-400">✓</span> : <span className="text-gray-700">✗</span>;
    return str.length > 80 ? str.slice(0, 77) + "…" : str;
}
