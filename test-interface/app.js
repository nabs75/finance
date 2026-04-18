/**
 * Skill Dashboard - Logic by Senior Web Dev
 */

const skillsData = [
    {
        id: 'senior-web-dev',
        title: 'Senior Web Dev',
        tag: 'Architecture',
        description: 'Expertise en orchestration de sous-agents, design systems et refactoring de haute précision.',
        version: '1.0.0',
        status: 'Actif'
    },
    {
        id: 'super-ui-ux-pro',
        title: 'Super UI/UX Pro',
        tag: 'Design',
        description: 'Conception d\'interfaces premium, accessibilité WCAG et micro-interactions fluides.',
        version: '1.0.0',
        status: 'Actif'
    },
    {
        id: 'skill-architect',
        title: 'Skill Architect',
        tag: 'Core',
        description: 'Agent spécialisé dans la création et l\'optimisation de nouvelles compétences pour Gemini CLI.',
        version: '2.5.0',
        status: 'Système'
    }
];

const renderSkills = () => {
    const grid = document.getElementById('skills-grid');
    
    // Simuler un léger délai de chargement pour l'effet visuel
    setTimeout(() => {
        grid.innerHTML = '';
        
        skillsData.forEach(skill => {
            const card = document.createElement('article');
            card.className = 'skill-card';
            card.setAttribute('tabindex', '0'); // Accessibilité clavier
            
            card.innerHTML = `
                <span class="skill-tag">${skill.tag}</span>
                <h2 class="skill-title">${skill.title}</h2>
                <p class="skill-desc">${skill.description}</p>
                <div class="skill-meta">
                    <span class="version">v${skill.version}</span>
                    <span class="status">${skill.status}</span>
                </div>
            `;
            
            card.addEventListener('click', () => {
                console.log(`Activation de la skill: ${skill.id}`);
                // Future extension : ouvrir un modal de détails
            });
            
            grid.appendChild(card);
        });
    }, 800);
};

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    renderSkills();
    
    const simulateBtn = document.getElementById('simulate-task');
    const terminalSection = document.getElementById('terminal-section');
    const terminalLogs = document.getElementById('terminal-logs');

    const addLog = (agent, msg, type = 'senior') => {
        const time = new Date().toLocaleTimeString();
        const line = document.createElement('div');
        line.className = 'log-line';
        line.innerHTML = `
            <span class="log-time">[${time}]</span>
            <span class="log-agent agent-${type}">${agent}</span>
            <span class="log-msg">${msg}</span>
        `;
        terminalLogs.appendChild(line);
        terminalLogs.scrollTop = terminalLogs.scrollHeight;
    };

    simulateBtn.addEventListener('click', () => {
        terminalSection.style.display = 'block';
        terminalLogs.innerHTML = '';
        simulateBtn.disabled = true;
        simulateBtn.innerText = 'Simulation en cours...';

        const sequence = [
            { agent: 'SYSTEM', msg: 'Démarrage de la simulation d\'orchestration...', type: 'core', delay: 0 },
            { agent: 'Senior Dev', msg: 'Analyse de la demande : "Créer un module de paiement sécurisé".', type: 'senior', delay: 1000 },
            { agent: 'Senior Dev', msg: 'Définition de l\'architecture modulaire et des interfaces TypeScript.', type: 'senior', delay: 2500 },
            { agent: 'UI/UX Pro', msg: 'Réception du brief. Conception de l\'interface de paiement (Focus A11y).', type: 'uiux', delay: 4000 },
            { agent: 'UI/UX Pro', msg: 'Génération de la palette de couleurs et des variables CSS.', type: 'uiux', delay: 5500 },
            { agent: 'Senior Dev', msg: 'Intégration du Design System et mise en place des tests unitaires.', type: 'senior', delay: 7000 },
            { agent: 'SYSTEM', msg: 'Simulation terminée avec succès. 100% Code Quality.', type: 'core', delay: 8500 }
        ];

        sequence.forEach(step => {
            setTimeout(() => {
                addLog(step.agent, step.msg, step.type);
                if (step.agent === 'SYSTEM' && step.msg.includes('terminée')) {
                    simulateBtn.disabled = false;
                    simulateBtn.innerText = 'Simuler une Tâche';
                }
            }, step.delay);
        });
    });
});
