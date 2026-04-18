import TelegramBot from 'node-telegram-bot-api';
import dotenv from 'dotenv';

dotenv.config();

const token = process.env.TELEGRAM_BOT_TOKEN;
const chatId = process.env.TELEGRAM_CHAT_ID;

let bot: TelegramBot | null = null;

if (token && chatId) {
    bot = new TelegramBot(token, { polling: false });
}

export const sendAlert = async (car: any) => {
    const message = `
🏎️ **NOUVEAU VÉHICULE TROUVÉ** 🏎️

📍 **Site :** ${car.site.toUpperCase()}
🏷️ **Titre :** ${car.title}
💰 **Prix :** ${car.price} €

🔗 [Voir l'annonce](${car.url})
    `;

    if (bot && chatId) {
        try {
            await bot.sendMessage(chatId, message, { parse_mode: 'Markdown' });
            console.log(`✅ Alerte envoyée pour: ${car.title}`);
        } catch (error) {
            console.error('❌ Erreur lors de l\'envoi de l\'alerte:', error);
        }
    } else {
        console.log('⚠️ Alerte (Console) :', message);
    }
};