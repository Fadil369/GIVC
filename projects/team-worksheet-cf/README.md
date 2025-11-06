# Team Worksheet - Cloudflare Edition

AI-powered team collaboration app for automated claim follow-ups, deployed on Cloudflare's global edge network.

## 🚀 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Global Edge (310+ cities)             │
├─────────────────────────────────────────────────────────┤
│  Cloudflare Pages (Frontend)                            │
│  └─ Next.js 14 + React 18 + Shadcn/ui                  │
│                                                          │
│  Cloudflare Workers (API)                               │
│  └─ Hono + D1 + KV + R2 + Durable Objects              │
│                                                          │
│  Cloudflare D1 (Database)                               │
│  └─ SQLite distributed globally                         │
│                                                          │
│  Cloudflare R2 (Storage)                                │
│  └─ Excel files + Attachments                           │
│                                                          │
│  Durable Objects (Real-time)                            │
│  └─ WebSocket collaboration                             │
└─────────────────────────────────────────────────────────┘
```

## ✨ Key Features

- 🤖 **AI-Powered Insights**: Smart priority scoring, auto-assignment, anomaly detection
- 🌍 **Global Edge Performance**: <50ms response times worldwide
- 📱 **Mobile + Web**: Progressive Web App + React Native mobile app
- 🔄 **Real-time Collaboration**: Live updates with WebSockets via Durable Objects
- 📊 **Excel Import/Export**: Seamless integration with existing workflows
- 🎨 **Beautiful UI**: Modern design with exceptional UX
- 🔐 **Enterprise Security**: JWT auth, row-level security, audit logging
- 📴 **Offline-First**: Works without internet, syncs automatically

## 📁 Project Structure

```
team-worksheet-cf/
├── workers/               # Cloudflare Workers backend
│   ├── src/
│   │   ├── index.ts      # Main worker entry
│   │   ├── routes/       # API route handlers
│   │   ├── db/           # D1 database schemas
│   │   ├── ai/           # AI scoring algorithms
│   │   └── durable/      # Durable Objects
│   ├── wrangler.toml     # Cloudflare configuration
│   └── package.json
│
├── web/                   # Next.js frontend
│   ├── app/              # App router pages
│   ├── components/       # React components
│   ├── lib/              # Utilities
│   └── public/
│
├── mobile/                # React Native app
│   ├── src/
│   ├── app.json
│   └── package.json
│
└── shared/                # Shared types and utilities
    ├── types/
    └── utils/
```

## 🛠️ Tech Stack

### Backend (Cloudflare Workers)
- **Framework**: Hono (ultra-fast edge framework)
- **Database**: Cloudflare D1 (distributed SQLite)
- **Storage**: Cloudflare R2 (S3-compatible object storage)
- **Cache**: Cloudflare KV (key-value store)
- **Real-time**: Durable Objects (WebSocket support)
- **Auth**: JWT with jose library

### Frontend (Cloudflare Pages)
- **Framework**: Next.js 14 with App Router
- **UI Library**: Shadcn/ui + Radix UI
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **Data Fetching**: TanStack Query (React Query)
- **State**: Zustand
- **Forms**: React Hook Form + Zod
- **Charts**: Recharts
- **Icons**: Lucide React

### Mobile (React Native)
- **Framework**: Expo
- **UI**: React Native Paper
- **Database**: WatermelonDB (offline-first)
- **Navigation**: React Navigation
- **State**: Zustand

## 🚦 Quick Start

### Prerequisites
```bash
npm install -g wrangler
npm install -g pnpm
```

### Backend Setup
```bash
cd workers
pnpm install

# Login to Cloudflare
wrangler login

# Create D1 database
wrangler d1 create team-worksheet-db

# Apply migrations
wrangler d1 migrations apply team-worksheet-db

# Start development server
pnpm dev
```

### Frontend Setup
```bash
cd web
pnpm install
pnpm dev
```

### Mobile Setup
```bash
cd mobile
pnpm install
expo start
```

## 📦 Deployment

### Deploy Backend
```bash
cd workers
wrangler deploy
```

### Deploy Frontend
```bash
cd web
pnpm build
wrangler pages deploy .next
```

## 🔑 Environment Variables

### Workers (.dev.vars)
```env
JWT_SECRET=your-secret-key
TEAMS_WEBHOOK_URL=https://...
OPENAI_API_KEY=sk-...  # For AI features
```

### Web (.env.local)
```env
NEXT_PUBLIC_API_URL=https://api.yourworker.workers.dev
NEXT_PUBLIC_WS_URL=wss://api.yourworker.workers.dev
```

## 📖 API Documentation

See [API_DOCS.md](./API_DOCS.md) for complete API reference.

## 🎨 Design System

See [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md) for UI/UX guidelines.

## 📄 License

Copyright © 2024 BrainSAIT LTD. All rights reserved.
