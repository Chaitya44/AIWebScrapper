"use client";

import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Shield, Zap, Globe, Lock } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useEffect } from "react";

const TRUST_POINTS = [
    { icon: Shield, text: "Your data stays in your browser — nothing stored on our servers" },
    { icon: Lock, text: "All scraping runs locally through your machine" },
    { icon: Zap, text: "Powered by Google Gemini 2.5 Flash AI" },
    { icon: Globe, text: "Works on any publicly accessible webpage" },
];

export default function LoginPage() {
    const router = useRouter();
    const { user, signInWithGoogle, signInWithGitHub } = useAuth();

    // Redirect if already logged in
    useEffect(() => {
        if (user) router.push("/");
    }, [user, router]);

    const handleGoogle = async () => {
        try {
            await signInWithGoogle();
            router.push("/");
        } catch (e: any) {
            console.error("[Auth] Google sign-in failed:", e.message);
        }
    };

    const handleGitHub = async () => {
        try {
            await signInWithGitHub();
            router.push("/");
        } catch (e: any) {
            console.error("[Auth] GitHub sign-in failed:", e.message);
        }
    };

    return (
        <div className="min-h-screen flex relative overflow-hidden">
            {/* Orbs */}
            <div className="orb" style={{ width: 600, height: 600, top: -200, left: -200, background: "rgba(16, 185, 129, 0.5)" }} />
            <div className="orb" style={{ width: 500, height: 500, bottom: -150, right: -150, background: "rgba(6, 182, 212, 0.4)", animationDelay: "-7s" }} />
            <div className="orb" style={{ width: 300, height: 300, top: "50%", left: "40%", background: "rgba(139, 92, 246, 0.3)", animationDelay: "-12s" }} />

            {/* ── LEFT PANEL — Branding + Trust ──────────────────── */}
            <div className="hidden lg:flex flex-col justify-center flex-1 pl-16 pr-12 relative z-10">
                <motion.div
                    initial={{ opacity: 0, x: -40 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.6 }}
                >
                    <h1 className="text-7xl font-extrabold tracking-tight leading-none mb-5">
                        <span className="text-transparent bg-clip-text bg-gradient-to-br from-emerald-300 via-teal-200 to-cyan-300">
                            Aria
                        </span>
                    </h1>
                    <p className="text-gray-400 text-xl leading-relaxed font-light max-w-md mb-12">
                        Extract structured data from any webpage.
                        No coding, no selectors, just paste a URL.
                    </p>

                    {/* Trust Points */}
                    <div className="space-y-4">
                        {TRUST_POINTS.map((tp, i) => (
                            <motion.div
                                key={tp.text}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.3 + i * 0.1 }}
                                className="flex items-center space-x-3"
                            >
                                <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/15 flex items-center justify-center flex-shrink-0">
                                    <tp.icon size={14} className="text-emerald-400" />
                                </div>
                                <span className="text-gray-500 text-sm">{tp.text}</span>
                            </motion.div>
                        ))}
                    </div>

                    {/* Animated decorative lines */}
                    <div className="mt-16 flex space-x-2">
                        {[0, 1, 2, 3, 4].map((i) => (
                            <motion.div
                                key={i}
                                className="h-1 rounded-full bg-gradient-to-r from-emerald-500/30 to-transparent"
                                initial={{ width: 0 }}
                                animate={{ width: 20 + Math.random() * 40 }}
                                transition={{ delay: 0.5 + i * 0.1, duration: 0.8 }}
                            />
                        ))}
                    </div>
                </motion.div>
            </div>

            {/* ── RIGHT PANEL — Login Card ───────────────────────── */}
            <div className="flex-1 flex items-center justify-center p-8 relative z-10">
                <motion.div
                    initial={{ opacity: 0, y: 30, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    transition={{ duration: 0.5, delay: 0.15 }}
                    className="w-full max-w-md"
                >
                    {/* Mobile logo (hidden on desktop) */}
                    <div className="lg:hidden text-center mb-8">
                        <h1 className="text-5xl font-extrabold">
                            <span className="text-transparent bg-clip-text bg-gradient-to-br from-emerald-300 via-teal-200 to-cyan-300">Aria</span>
                        </h1>
                        <p className="text-gray-500 text-sm mt-2">AI-powered web data extraction</p>
                    </div>

                    {/* Card */}
                    <div className="glass-card gradient-border rounded-2xl p-8 space-y-6">
                        <div className="text-center">
                            <h2 className="text-white text-xl font-bold mb-1">Welcome to Aria</h2>
                            <p className="text-gray-500 text-sm">Choose a provider to get started</p>
                        </div>

                        <div className="space-y-3">
                            {/* Google */}
                            <button
                                onClick={handleGoogle}
                                className="w-full flex items-center justify-center space-x-3 bg-white hover:bg-gray-50 text-gray-800 font-medium py-4 px-5 rounded-xl transition-all duration-200 shadow-sm hover:shadow-md group"
                            >
                                <svg width="20" height="20" viewBox="0 0 24 24">
                                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" />
                                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                                </svg>
                                <span className="text-sm">Continue with Google</span>
                            </button>

                            {/* GitHub */}
                            <button
                                onClick={handleGitHub}
                                className="w-full flex items-center justify-center space-x-3 bg-[#161b22] hover:bg-[#1f2937] text-white font-medium py-4 px-5 rounded-xl transition-all duration-200 border border-white/[0.08] hover:border-white/[0.15] group"
                            >
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="white">
                                    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z" />
                                </svg>
                                <span className="text-sm">Continue with GitHub</span>
                            </button>
                        </div>

                        {/* Divider */}
                        <div className="flex items-center space-x-3">
                            <div className="flex-1 h-px bg-white/[0.06]" />
                            <Shield size={13} className="text-gray-600" />
                            <div className="flex-1 h-px bg-white/[0.06]" />
                        </div>

                        {/* Security notice */}
                        <div className="bg-emerald-500/5 border border-emerald-500/10 rounded-xl p-4">
                            <div className="flex items-start space-x-2.5">
                                <Lock size={14} className="text-emerald-500 mt-0.5 flex-shrink-0" />
                                <div>
                                    <p className="text-emerald-400 text-xs font-semibold mb-1">Privacy-first architecture</p>
                                    <p className="text-gray-500 text-[11px] leading-relaxed">
                                        All data processing happens locally. Your extraction history syncs
                                        securely to your account via Firebase.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <p className="text-gray-600 text-[11px] text-center">
                            By signing in, you agree to our{" "}
                            <a href="/terms" className="text-emerald-500/60 hover:text-emerald-400 transition-colors">Terms</a>
                            {" "}and{" "}
                            <a href="/privacy" className="text-emerald-500/60 hover:text-emerald-400 transition-colors">Privacy Policy</a>
                        </p>
                    </div>
                </motion.div>
            </div>
        </div>
    );
}
