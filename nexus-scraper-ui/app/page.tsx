"use client";

import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import NexusDashboard from "@/components/NexusDashboard";

export default function Home() {
    const { user, loading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!loading && !user) {
            router.push("/login");
        }
    }, [user, loading, router]);

    // Show nothing while checking auth
    if (loading || !user) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="w-8 h-8 rounded-full border-2 border-emerald-500/30 border-t-emerald-500 animate-spin" />
            </div>
        );
    }

    return <NexusDashboard />;
}
