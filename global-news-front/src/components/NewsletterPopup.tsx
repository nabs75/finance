'use client';
import { useState, useEffect } from 'react';
import { X } from 'lucide-react';

export default function NewsletterPopup() {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        const timer = setTimeout(() => {
            const dismissed = localStorage.getItem('newsletter_dismissed');
            if (!dismissed) setIsVisible(true);
        }, 5000); // Apparaît après 5 secondes
        return () => clearTimeout(timer);
    }, []);

    const close = () => {
        setIsVisible(false);
        localStorage.setItem('newsletter_dismissed', 'true');
    };

    if (!isVisible) return null;

    return (
        <div class="fixed bottom-8 right-8 z-50 animate-in fade-in slide-in-from-bottom-10 duration-500">
            <div class="bg-card border border-white/10 p-8 rounded-3xl shadow-2xl max-w-sm relative">
                <button onClick={close} class="absolute top-4 right-4 text-gray-500 hover:text-white">
                    <X size={20} />
                </button>
                <h3 class="text-2xl font-bold mb-2">Restez informé 📬</h3>
                <p class="text-gray-400 text-sm mb-6">
                    Recevez chaque matin le résumé des actualités mondiales décryptées par notre IA.
                </p>
                <form class="flex flex-col gap-3">
                    <input 
                        type="email" 
                        placeholder="votre@email.com" 
                        class="bg-background border border-white/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-accent transition-colors"
                        required
                    />
                    <button class="bg-accent hover:bg-accent/90 text-white font-bold py-3 rounded-xl transition-all">
                        S'abonner gratuitement
                    </button>
                </form>
            </div>
        </div>
    );
}