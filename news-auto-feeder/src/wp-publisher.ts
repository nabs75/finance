import axios from 'axios';
import dotenv from 'dotenv';
import { Article } from './ai-rewriter';

dotenv.config();

const WP_URL = process.env.WP_URL; // ex: https://mon-site.com/wp-json/wp/v2/posts
const WP_USER = process.env.WP_USER;
const WP_APP_PASSWORD = process.env.WP_APP_PASSWORD; // Mot de passe d'application WP

export const publishToWordPress = async (article: Article) => {
    console.log(`📤 Publication sur WordPress : ${article.title}`);

    if (!WP_URL || !WP_USER || !WP_APP_PASSWORD) {
        console.log('⚠️ WordPress non configuré. Affichage console uniquement.');
        return true;
    }

    const auth = Buffer.from(`${WP_USER}:${WP_APP_PASSWORD}`).toString('base64');

    try {
        await axios.post(WP_URL, {
            title: article.title,
            content: article.content,
            status: 'publish', // ou 'draft' pour relecture manuelle
            excerpt: `Source originale : ${article.source}`,
            meta: {
                original_url: article.url
            }
        }, {
            headers: {
                'Authorization': `Basic ${auth}`,
                'Content-Type': 'application/json'
            }
        });

        console.log('✅ Article publié avec succès !');
        return true;
    } catch (error) {
        console.error('❌ Erreur de publication WordPress :', error);
        return false;
    }
};