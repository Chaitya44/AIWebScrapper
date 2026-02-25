"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Sun, Moon, User, Sparkles, LogOut } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

export default function Header() {
    const pathname = usePathname();
    const { user, signOut } = useAuth();
    const [theme, setTheme] = useState<"dark" | "light">("dark");
    const [showMenu, setShowMenu] = useState(false);

    useEffect(() => {
        const saved = localStorage.getItem("aria_theme") as "dark" | "light" | null;
        if (saved) {
            setTheme(saved);
            document.documentElement.classList.toggle("light", saved === "light");
        }
    }, []);

    const toggleTheme = () => {
        const next = theme === "dark" ? "light" : "dark";
        setTheme(next);
        localStorage.setItem("aria_theme", next);
        document.documentElement.classList.toggle("light", next === "light");
    };

    if (pathname === "/login") return null;

    const isDark = theme === "dark";

    return (
        <header className="sticky top-0 z-50 w-full header-bar">
            <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
                {/* Left — Logo + Nav */}
                <div className="flex items-center space-x-8">
                    <Link href="/" className="flex items-center space-x-2">
                        <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center">
                            <Sparkles size={14} className="text-white" />
                        </div>
                        <span className="text-lg font-bold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">
                            Aria
                        </span>
                    </Link>

                    <nav className="hidden md:flex items-center space-x-1">
                        {[
                            { href: "/", label: "Dashboard" },
                            { href: "/privacy", label: "Privacy" },
                            { href: "/terms", label: "Terms" },
                        ].map((link) => (
                            <Link
                                key={link.href}
                                href={link.href}
                                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 nav-link ${pathname === link.href ? "nav-link-active" : ""
                                    }`}
                            >
                                {link.label}
                            </Link>
                        ))}
                    </nav>
                </div>

                {/* Right — Theme + User */}
                <div className="flex items-center space-x-2">
                    <button
                        onClick={toggleTheme}
                        className="w-9 h-9 rounded-xl theme-toggle-btn flex items-center justify-center transition-all duration-200"
                        title={`Switch to ${isDark ? "light" : "dark"} mode`}
                    >
                        {isDark ? <Sun size={15} className="text-gray-400" /> : <Moon size={15} className="text-gray-600" />}
                    </button>

                    {user ? (
                        /* Logged in — show avatar with dropdown */
                        <div className="relative">
                            <button
                                onClick={() => setShowMenu(!showMenu)}
                                className="w-9 h-9 rounded-xl overflow-hidden border-2 border-emerald-500/30 hover:border-emerald-500/60 transition-all duration-200"
                            >
                                {user.photoURL ? (
                                    <img src={user.photoURL} alt="" className="w-full h-full object-cover" />
                                ) : (
                                    <div className="w-full h-full bg-gradient-to-br from-emerald-500/20 to-teal-500/20 flex items-center justify-center">
                                        <span className="text-emerald-400 text-xs font-bold">
                                            {user.displayName?.charAt(0) || user.email?.charAt(0) || "?"}
                                        </span>
                                    </div>
                                )}
                            </button>

                            {showMenu && (
                                <div className="absolute right-0 top-12 w-56 glass-card rounded-xl border border-white/[0.06] p-3 space-y-2 shadow-xl z-50">
                                    <div className="px-2 py-1">
                                        <p className="text-white text-sm font-medium truncate">{user.displayName || "User"}</p>
                                        <p className="text-gray-500 text-xs truncate">{user.email}</p>
                                    </div>
                                    <div className="h-px bg-white/[0.06]" />
                                    <button
                                        onClick={async () => {
                                            setShowMenu(false);
                                            await signOut();
                                        }}
                                        className="w-full flex items-center space-x-2 px-2 py-2 rounded-lg text-red-400 hover:bg-red-500/10 transition-colors text-sm"
                                    >
                                        <LogOut size={14} />
                                        <span>Sign out</span>
                                    </button>
                                </div>
                            )}
                        </div>
                    ) : (
                        /* Not logged in — show login button */
                        <Link
                            href="/login"
                            className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 border border-emerald-500/20 flex items-center justify-center transition-all duration-200 hover:from-emerald-500/30 hover:to-teal-500/30"
                        >
                            <User size={15} className="text-emerald-400" />
                        </Link>
                    )}
                </div>
            </div>
        </header>
    );
}
