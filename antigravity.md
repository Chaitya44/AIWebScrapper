This is the final, definitive frontend overhaul.

The "Black Text" issue is happening because browser default stylesheets are overriding your Tailwind classes. The "Bare Minimum" look is because you are using flat colors without **Depth** (Shadows, Glows, Gradients) or **Motion**.

Here is `ANTIGRAVITY_UI_MASTER_UPGRADE.md`. This file contains the "Nuclear" CSS fix and a complete React component code that replaces your current dashboard with a high-end, animated "Command Center."

### 📄 `ANTIGRAVITY_UI_MASTER_UPGRADE.md`

```markdown
# 🎨 UI Master Protocol: The "Nexus Prime" Upgrade

## 🚨 CRITICAL FIX: The Visibility Patch
**Problem:** Data text renders as black on black.
**Root Cause:** Browser user-agent styles are overriding utility classes.
**Solution:** We inject a "Nuclear" CSS layer that forces text color at the element level using `!important`.

### 🛠️ Step 1: Update `app/globals.css`
Delete your current table styles and append this **EXACT** block at the bottom of your CSS file.

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* --- ☢️ THE NUCLEAR VISIBILITY FIX ☢️ --- */
@layer utilities {
  /* Force the background to be deep void black, not just 'dark' */
  body {
    background-color: #030304; 
    background-image: 
      radial-gradient(circle at 50% 0%, rgba(0, 255, 148, 0.03) 0%, transparent 50%),
      linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
    background-size: 100% 100%, 40px 40px, 40px 40px;
  }

  /* Force Table Text Colors */
  .nexus-table th {
    color: #00ff94 !important; /* Neon Green Headers */
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    background-color: rgba(255, 255, 255, 0.05);
    padding: 1rem;
  }

  .nexus-table td {
    color: #e2e8f0 !important; /* Bright White-Grey Data */
    font-family: 'Courier New', monospace;
    padding: 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  }

  /* Force Links to stand out */
  .nexus-table a {
    color: #38bdf8 !important; /* Cyan Blue */
    text-decoration: none;
    border-bottom: 1px dotted #38bdf8;
  }
  
  .nexus-table tr:hover td {
    background-color: rgba(0, 255, 148, 0.05); /* Subtle Green Hover */
    transition: background-color 0.2s ease;
  }
}

```

---

## 💎 Step 2: The "Nexus Prime" Dashboard Component

**Goal:** Replace the "bare minimum" look with a glass-morphic, animated interface.
**Tech:** Framer Motion + Lucide Icons.

**Action:** Create `components/NexusDashboard.tsx` and paste this code.

```tsx
"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Terminal, Cpu, Shield, Zap, Search, Download, ChevronRight } from "lucide-react";

export default function NexusDashboard() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [elapsed, setElapsed] = useState(0.0);

  // Fake logs for the "Cinema" effect
  const addLog = (msg: string) => setLogs((prev) => [...prev.slice(-4), msg]);

  const handleScrape = async () => {
    setLoading(true);
    setLogs(["[SYSTEM] Initializing Neural Handshake...", "[NET] Bypassing Cloudflare Gateways..."]);
    setElapsed(0);
    
    // Timer Animation
    const timer = setInterval(() => setElapsed((p) => p + 0.1), 100);

    try {
      const res = await fetch("http://localhost:8000/api/scrape", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, config: { stealthMode: true } }),
      });
      const json = await res.json();
      
      clearInterval(timer);
      setLoading(false);
      setData(json.entities);
      addLog(`[SUCCESS] Extracted ${json.totalItems} entities in ${elapsed.toFixed(1)}s`);
    } catch (e) {
      clearInterval(timer);
      setLoading(false);
      addLog("[ERROR] Connection Severed.");
    }
  };

  return (
    <div className="min-h-screen p-8 text-gray-200 font-sans flex flex-col items-center">
      
      {/* 1. THE HEADER (Animated Entry) */}
      <motion.div 
        initial={{ y: -50, opacity: 0 }} 
        animate={{ y: 0, opacity: 1 }} 
        className="text-center mb-12"
      >
        <h1 className="text-5xl font-bold tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-500 mb-2">
          NEXUS // PRIME
        </h1>
        <p className="text-gray-500 text-sm tracking-widest uppercase">
          Autonomous Web Intelligence Engine v2.0
        </p>
      </motion.div>

      {/* 2. THE TERMINAL WINDOW (Glassmorphism) */}
      <motion.div 
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="w-full max-w-5xl bg-black/40 backdrop-blur-xl border border-white/10 rounded-xl overflow-hidden shadow-[0_0_50px_rgba(0,255,148,0.05)]"
      >
        {/* Window Controls */}
        <div className="h-10 bg-white/5 border-b border-white/5 flex items-center px-4 justify-between">
          <div className="flex space-x-2">
            <div className="w-3 h-3 rounded-full bg-red-500/80" />
            <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
            <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
          </div>
          <div className="flex items-center space-x-2 text-xs text-gray-500 font-mono">
            <Shield size={12} />
            <span>SECURE_CONNECTION_ESTABLISHED</span>
          </div>
        </div>

        {/* Input Zone */}
        <div className="p-8 space-y-6">
          <div className="relative group">
            <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-500 group-focus-within:text-emerald-400 transition-colors" />
            </div>
            <input 
              type="text" 
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="ENTER TARGET URL PROTOCOL..." 
              className="w-full bg-black/50 border border-white/10 rounded-lg py-4 pl-12 pr-4 text-emerald-400 font-mono focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-all placeholder:text-gray-700"
            />
            <button 
              onClick={handleScrape}
              disabled={loading}
              className="absolute right-2 top-2 bottom-2 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 px-6 rounded-md font-bold text-xs tracking-wider border border-emerald-500/20 transition-all"
            >
              {loading ? "SCANNING..." : "INITIATE SCAN"}
            </button>
          </div>

          {/* System Logs (The Terminal) */}
          <div className="h-32 bg-black/80 rounded-lg border border-white/5 p-4 font-mono text-xs text-gray-400 overflow-hidden relative">
            {logs.map((log, i) => (
              <motion.div 
                key={i} 
                initial={{ opacity: 0, x: -10 }} 
                animate={{ opacity: 1, x: 0 }}
                className="mb-1"
              >
                <span className="text-emerald-500/50 mr-2">➜</span> {log}
              </motion.div>
            ))}
            {loading && (
              <div className="absolute bottom-4 right-4 text-4xl font-mono text-white/5">
                {elapsed.toFixed(1)}s
              </div>
            )}
          </div>
        </div>
      </motion.div>

      {/* 3. DATA RESULTS (Animated Grid) */}
      <div className="w-full max-w-5xl mt-8">
        <AnimatePresence>
          {data && Object.entries(data).map(([category, items]: [string, any], idx) => (
            <motion.div
              key={category}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="mb-8"
            >
              <div className="flex items-center space-x-2 mb-4">
                <Cpu className="text-emerald-400" size={16} />
                <h2 className="text-lg font-bold text-white uppercase tracking-wider">{category.replace(/_/g, " ")}</h2>
                <span className="text-xs bg-white/10 px-2 py-0.5 rounded text-gray-400">
                  {Array.isArray(items) ? items.length : 1} NODES
                </span>
              </div>

              {/* THE TABLE - Uses the Nuclear CSS class 'nexus-table' */}
              <div className="bg-black/40 border border-white/10 rounded-lg overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="nexus-table w-full text-left">
                    <thead>
                      <tr>
                        {Array.isArray(items) && items.length > 0 && 
                          Object.keys(items[0]).slice(0, 5).map((header) => (
                            <th key={header}>{header}</th>
                          ))
                        }
                      </tr>
                    </thead>
                    <tbody>
                      {Array.isArray(items) ? items.slice(0, 10).map((row, rIdx) => (
                        <tr key={rIdx}>
                          {Object.values(row).slice(0, 5).map((val: any, cIdx) => (
                            <td key={cIdx}>{String(val).slice(0, 50)}</td>
                          ))}
                        </tr>
                      )) : (
                        // Single Object View
                        <tr><td><pre>{JSON.stringify(items, null, 2)}</pre></td></tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
      
    </div>
  );
}

```

---

## 🚀 Execution Guide

1. **Paste** the CSS into `globals.css` (This fixes the black text).
2. **Paste** the Component code into `components/NexusDashboard.tsx`.
3. **Update** your `app/page.tsx` to simply import and render `<NexusDashboard />`.
4. **Install Icons:** `npm install lucide-react framer-motion`

**Result:** You will now have a glowing, animated, "Matrix-style" interface where the text is perfectly visible (White on Black) and the waiting time is visualized by a running timer.