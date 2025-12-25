# TaskMitra - Clean Frontend

A modern, production-ready React application for TaskMitra workflow orchestration platform. This is a clean implementation without Lovable-specific dependencies.

## Tech Stack

- **React 18** with TypeScript
- **Vite** - Lightning-fast build tool
- **Tailwind CSS** - Utility-first styling
- **Shadcn UI** - Beautifully designed components
- **React Router** - Client-side routing
- **TanStack Query** - Server state management
- **Axios** - HTTP client with token refresh
- **React Toastify** - Toast notifications

## Getting Started

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:8080`

### Build for Production

```bash
npm run build
```

## Project Structure

```
src/
├── components/
│   ├── auth/          # Authentication components
│   ├── chat/          # Chat-related components
│   ├── layout/        # Layout components (Navbar, ThemeToggle)
│   ├── settings/      # Settings modal & panels
│   └── ui/            # Shadcn UI components
├── contexts/          # React contexts (Auth, Chat)
├── hooks/             # Custom React hooks
├── lib/               # Utilities & API clients
├── pages/             # Page components
└── App.tsx            # Main app component
```

## Features

- 🔐 **Authentication** - JWT-based auth with automatic token refresh
- 💬 **Chat Interface** - Real-time workflow orchestration
- 🎨 **Dark Mode** - Built-in theme switching
- 🔌 **OAuth Integration** - Google/Gmail connections
- 📱 **Responsive Design** - Mobile-first approach
- ⚡ **Optimized Performance** - Code splitting & lazy loading

## Environment Variables

Create a `.env` file if needed for custom configurations. The app connects to `http://localhost:8000/api/v1` by default.

## License

All rights reserved © 2025 TaskMitra
