# InterviewAI Coach

<p align="center">
  <strong>Préparez vos entretiens d'embauche avec l'intelligence artificielle.</strong>
</p>

<p align="center">
  Une plateforme intelligente qui accompagne les candidats dans leur préparation aux entretiens professionnels grâce à des questions personnalisées générées à partir de leur CV et de l'offre d'emploi ciblée.
</p>

---

## À propos du projet

**InterviewAI Coach** est une application web SaaS conçue pour aider les candidats à mieux préparer leurs entretiens d'embauche grâce à l'intelligence artificielle.

L'application exploite les informations du CV et de l'offre d'emploi pour générer des questions d'entretien adaptées au profil, aux compétences et au poste recherché.

L'objectif est de proposer une expérience de préparation personnalisée, interactive et évolutive, permettant aux candidats de s'entraîner, de conserver leurs réponses et, à terme, d'améliorer leurs performances grâce à des analyses intelligentes.

## Objectifs

- Faciliter la préparation aux entretiens d'embauche.
- Personnaliser les questions selon le profil du candidat.
- Exploiter les CV et les offres d'emploi pour contextualiser les simulations.
- Permettre aux utilisateurs de s'entraîner dans un environnement interactif.
- Conserver l'historique des simulations et les réponses.
- Accompagner progressivement les candidats dans l'amélioration de leurs performances.

## Fonctionnalités

### Fonctionnalités développées

- **Authentification** — Inscription, connexion et gestion du compte utilisateur.
- **Profil utilisateur** — Gestion des informations personnelles.
- **Gestion des CV** — Importation et stockage des CV au format PDF.
- **Gestion des offres d'emploi** — Importation et gestion des offres.
- **Extraction de contenu PDF** — Récupération du texte des documents.
- **Préparation personnalisée** — Association d'un CV et d'une offre d'emploi pour créer un contexte de préparation.
- **Génération de questions par IA** — Création de questions adaptées au profil et au poste visé.
- **Simulation d'entretien textuelle** — Questions et réponses saisies par l'utilisateur.
- **Persistance des réponses** — Enregistrement des réponses dans la base de données.

### Fonctionnalités en cours et prévues

- Historique complet des entretiens.
- Consultation détaillée des questions et réponses.
- Reprise des simulations inachevées.
- Analyse intelligente des réponses.
- Évaluation et notation des performances.
- Recommandations personnalisées pour améliorer les réponses.
- Tableau de bord de progression.
- Simulation d'entretien vocal.
- Reconnaissance et transcription de la voix.

## Technologies utilisées

| Domaine | Technologies |
|---|---|
| Backend | Python, FastAPI |
| Frontend | TypeScript |
| Base de données | PostgreSQL |
| Intelligence artificielle | Google Gemini API |
| Documents | Extraction de texte PDF |
| Conteneurisation | Docker, Docker Compose |
| Gestion de versions | Git, GitHub |

> La stack frontend et le système de base de données seront précisés selon les dépendances et la configuration réelles du dépôt.

## Architecture du projet

InterviewAI Coach repose sur une architecture séparant les responsabilités du frontend, du backend, de la base de données et du service d'intelligence artificielle.

```text
InterviewAI-Coach/
│
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routes/
│   │   ├── services/
│   │   └── ...
│   ├── requirements.txt
│   └── ...
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── ...
│
├── docker-compose.yml
├── .env.example
└── README.md
```

*Cette arborescence est indicative : elle devra être adaptée à l'organisation réelle du dépôt.*

## Installation et configuration

### 1. Prérequis

Avant de commencer, installer :

- Git
- Python 3
- Node.js et npm
- Docker et Docker Compose (si utilisés)
- Une clé API Google Gemini

### 2. Cloner le dépôt

```bash
git clone https://github.com/VOTRE-USERNAME/InterviewAI-Coach.git

cd InterviewAI-Coach
```

### 3. Configurer les variables d'environnement

Créer les fichiers `.env` nécessaires à partir des exemples fournis dans le projet.

Exemple de configuration :

```env
GEMINI_API_KEY=votre_cle_api
```

Les autres variables nécessaires (base de données, authentification, configuration du serveur) doivent être renseignées selon les fichiers de configuration du projet.

**Important : ne jamais publier les clés API, mots de passe ou autres secrets dans un dépôt GitHub.**

### 4. Lancer le backend

Se placer dans le dossier backend :

```bash
cd backend
```

Créer un environnement virtuel :

```bash
python -m venv venv
```

Activer l'environnement virtuel sous Linux :

```bash
source venv/bin/activate
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

Lancer le serveur FastAPI :

```bash
uvicorn app.main:app --reload
```

La documentation interactive de l'API est généralement accessible à l'adresse :

```text
http://127.0.0.1:8000/docs
```

### 5. Lancer le frontend

Dans un autre terminal :

```bash
cd frontend
```

Installer les dépendances :

```bash
npm install
```

Lancer le serveur de développement :

```bash
npm run dev
```

L'adresse locale du frontend dépend de la configuration du projet et du framework utilisé.

## Docker

Le projet prévoit également une approche de conteneurisation avec Docker afin de faciliter la configuration et le déploiement de l'application.

Lorsque le fichier `docker-compose.yml` est configuré pour l'ensemble des services :

```bash
docker compose up --build
```

Pour arrêter les services :

```bash
docker compose down
```

## Parcours utilisateur

Le fonctionnement général d'InterviewAI Coach suit ce parcours :

1. L'utilisateur crée un compte et se connecte.
2. Il importe son CV.
3. Il importe une offre d'emploi.
4. Il crée une préparation en associant les deux documents.
5. L'intelligence artificielle analyse le contexte et génère des questions personnalisées.
6. L'utilisateur démarre une simulation d'entretien.
7. Il répond aux questions.
8. Ses réponses sont enregistrées pour permettre leur consultation et leur exploitation ultérieure.
9. Les futures fonctionnalités d'analyse permettront d'obtenir des retours personnalisés et de suivre sa progression.

## Feuille de route

- [x] Authentification et gestion des utilisateurs
- [x] Gestion du profil utilisateur
- [x] Importation des CV
- [x] Importation des offres d'emploi
- [x] Extraction du contenu PDF
- [x] Création des préparations
- [x] Génération de questions personnalisées avec l'IA
- [x] Simulation d'entretien textuelle
- [x] Enregistrement des réponses
- [ ] Historique des simulations
- [ ] Consultation détaillée des résultats
- [ ] Reprise des sessions inachevées
- [ ] Analyse IA des réponses
- [ ] Évaluation des performances
- [ ] Conseils et recommandations personnalisés
- [ ] Tableau de bord de progression
- [ ] Simulation vocale
- [ ] Transcription automatique des réponses

## Sécurité

La sécurité des données utilisateurs est un élément important du projet.

Les principes à respecter comprennent :

- Protection des routes nécessitant une authentification.
- Isolation des données entre utilisateurs.
- Protection des informations personnelles.
- Stockage sécurisé des clés API.
- Validation des fichiers importés.
- Gestion appropriée des erreurs et des accès non autorisés.

## Vision du projet

InterviewAI Coach ambitionne de devenir un véritable assistant personnel de préparation aux entretiens d'embauche.

Au-delà de la simple génération de questions, la vision est de proposer un accompagnement intelligent capable de comprendre le profil d'un candidat, de simuler des situations professionnelles réalistes, d'évaluer ses réponses et de l'aider à progresser au fil de ses entraînements.

**L'objectif : transformer chaque préparation en une opportunité de progresser et d'aborder son prochain entretien avec davantage de confiance.**

---

## Auteur

**Projet : InterviewAI Coach**

Développé dans le cadre d'un projet personnel de conception et de développement d'une application SaaS intégrant l'intelligence artificielle.

---

<p align="center">
  <strong>InterviewAI Coach — Prepare smarter. Interview better.</strong>
</p>
