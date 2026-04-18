import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import NewsTicker from "@/components/NewsTicker";
import NewsletterPopup from "@/components/NewsletterPopup";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Global News Hub | Actualités Mondiales",
  description: "L'actualité mondiale décryptée et traduite par l'IA.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" class="dark">
      <body class={`${inter.className} bg-background text-white antialiased`}>
        <NewsTicker />
        <header class="border-b border-white/10 py-6">
          <div class="container mx-auto px-4 flex justify-between items-center">
            <h1 class="text-2xl font-bold tracking-tighter">GLOBAL <span class="text-accent">NEWS HUB</span></h1>
            <nav class="hidden md:flex gap-6 text-sm font-medium text-gray-400">
              <a href="#" class="hover:text-white">Monde</a>
              <a href="#" class="hover:text-white">Technologie</a>
              <a href="#" class="hover:text-white">Économie</a>
            </nav>
          </div>
        </header>
        {children}
        <NewsletterPopup />
        <footer class="border-t border-white/10 py-12 mt-20 text-center text-gray-500 text-sm">      
          <p>&copy; 2026 Global News Hub - Propulsé par Super IA</p>
        </footer>
      </body>
    </html>
  );
}