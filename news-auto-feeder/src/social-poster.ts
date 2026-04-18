import { TwitterApi } from 'twitter-api-v2';
import dotenv from 'dotenv';
import { Article } from './ai-rewriter';
import axios from 'axios';

dotenv.config();

const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const API_URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${GEMINI_API_KEY}`;

// Configuration Twitter
const twitterClient = new TwitterApi({
    appKey: process.env.TWITTER_APP_KEY || '',
    appSecret: process.env.TWITTER_APP_SECRET || '',
    accessToken: process.env.TWITTER_ACCESS_TOKEN || '',
    accessSecret: process.env.TWITTER_ACCESS_SECRET || '',
});

export const postToSocialMedia = async (article: Article) => {
    console.log(`📱 Génération de post social pour : ${article.title}`);

    const prompt = `
    Génère un tweet percutant et engageant pour promouvoir l'article suivant.
    L'article s'intitule : "${article.title}"
    Le contenu est : "${article.content.substring(0, 500)}..."
    
    CONSIGNES :
    - Moins de 280 caractères.
    - Utilise des emojis pertinents.
    - Ajoute 3 hashtags stratégiques.
    - Inclut un appel à l'action court.

    Répond uniquement avec le texte du tweet.
    `;

    try {
        const response = await axios.post(API_URL, {
            contents: [{ parts: [{ text: prompt }] }]
        });

        const tweetContent = response.data.candidates[0].content.parts[0].text;
        const finalTweet = `${tweetContent}\n\nEn savoir plus : ${article.url}`;

        if (process.env.TWITTER_ACCESS_TOKEN) {
            await twitterClient.v2.tweet(finalTweet);
            console.log('✅ Tweet publié avec succès !');
        } else {
            console.log('⚠️ Twitter non configuré. Simulation du tweet :\n', finalTweet);
        }
    } catch (error) {
        console.error('❌ Erreur lors de la publication sociale :', error);
    }
};