import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const API_URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${GEMINI_API_KEY}`;

export interface Article {
    title: string;
    content: string;
    source: string;
    url: string;
}

export const rewriteArticle = async (article: Article): Promise<Article | null> => {
    console.log(`🧠 Réécriture IA : ${article.title}`);

    const prompt = `
    Agis en tant que journaliste senior pour un grand média francophone. 
    Ta mission est de traduire et de réécrire l'article suivant pour un public francophone.
    
    CONSIGNES :
    1. Ton : Professionnel, factuel et engageant.
    2. Format : Un titre accrocheur, un court chapeau introductif, et le corps de l'article structuré en paragraphes.
    3. Contenu : Ne traduis pas mot à mot. Synthétise les points clés et rends le texte fluide.
    4. Langue cible : Français.
    5. Mentionne la source originale discrètement à la fin.

    TITRE ORIGINAL : ${article.title}
    CONTENU ORIGINAL : ${article.content}

    RÉPOND UNIQUEMENT AU FORMAT JSON SUIVANT :
    {
        "title": "Nouveau titre en français",
        "content": "Contenu complet réécrit en HTML (utilisant <p>, <h2>, etc.)"
    }
    `;

    try {
        const response = await axios.post(API_URL, {
            contents: [{ parts: [{ text: prompt }] }]
        });

        const resultText = response.data.candidates[0].content.parts[0].text;
        // Nettoyage si l'IA ajoute des backticks ```json
        const cleanJson = resultText.replace(/```json|```/g, '').trim();
        const rewritten = JSON.parse(cleanJson);

        return {
            ...article,
            title: rewritten.title,
            content: rewritten.content
        };
    } catch (error) {
        console.error(`❌ Erreur IA sur ${article.title}:`, error);
        return null;
    }
};