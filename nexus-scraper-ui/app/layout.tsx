import type { Metadata } from "next";
import "./globals.css";
import Header from "@/components/Header";

export const metadata: Metadata = {
    title: "Aria — AI Web Data Extractor",
    description: "Universal web data extraction powered by Google Gemini AI and DrissionPage",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <body className="antialiased">
                <Header />
                {children}
            </body>
        </html>
    );
}
