🌿 BranchBlog — Multimodal AI-Powered Blog Platform

A modern, multimodal blogging experience that combines Flask, Streamlit, and Gemini AI to create, explore, and interact with content like never before.

This project includes both:

A Flask backend API for posts

A Streamlit multimodal front-end with AI generation & unique social features

Ready-to-run frontend (AI Studio app scaffold included)

🚀 Features
📝 Core Blog Features

Create, view, and manage posts

Manage data via a lightweight Flask API

Streamlit UI for browsing and interacting with posts

🤖 Multimodal AI Features

Generate blog posts from text, images, voice, or mixed inputs

Smart post enhancement: tags, summaries, captions, hashtags

Grammarly-like AI suggestions

Image-to-blog and audio-to-blog modes

🆕 Unique Social Features (Not found in Instagram or Facebook!)

Branch-Reply System – every post can “branch” into multiple parallel narratives

Mood-Heatmap – visualizes emotional tone across your posts

Time-Capsule Posts – lock posts so they open in the future

Perspective-Swap AI – rewrite posts from alternate viewpoints

Parallel-Persona Threads – generate alternative versions of yourself writing the same post

🛠️ Tech Stack
Frontend

React + TypeScript (Vite)

Streamlit (for multimodal + deployment mode)

Tailwind-ready UI structure

Backend

Flask API (/api/posts)

In-memory JSON datastore (or extendable to DB)

AI

Gemini API (set your key in .env.local)

📁 Project Structure
project/
│
├── components/          # React UI components
├── services/            # API & AI service wrappers
├── App.tsx              # Root app
├── index.tsx            # Entry point
├── vite.config.ts       # Vite config
├── types.ts             # Shared TypeScript types
├── package.json
├── tsconfig.json
├── .env.local           # Add your GEMINI_API_KEY here
└── README.md

▶️ Run Locally
Prerequisites

Node.js (LTS recommended)

Gemini API Key (from Google AI Studio)

Steps

Install dependencies

npm install


Add your Gemini key in .env.local

GEMINI_API_KEY=your_key_here


Start development server

npm run dev


Open the app

http://localhost:5173

🌐 Deploy (Streamlit)

This project is optimized for streamlit.io deployment.
Upload your files → Set environment variable → Deploy instantly.

📌 AI Studio App Link

(If you want this rewritten or removed, I can adjust it.)

https://ai.studio/apps/drive/19lsK3_jUQ_8lENftt0kWrKHl9jclxAGe

🤝 Contributing

PRs welcome!
If you want GitHub Actions CI/CD, I can generate it.

📄 License

MIT — use freely.
