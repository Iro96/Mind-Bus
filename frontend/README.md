# Mind-Bus Frontend

Vue 3 + TypeScript frontend for the Mind-Bus AI Agent Platform.

## Features

- **Modern Chat Interface** - Real-time chat with the AI agent
- **Memory Management** - View and manage long-term and episodic memories
- **Document Management** - Upload and manage documents for RAG
- **Tool Integration** - Control and monitor available tools
- **Dark Theme** - Beautiful dark mode optimized for extended use
- **Responsive Design** - Works on desktop and mobile

## Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Build

```bash
npm run build
```

Production-ready files will be in the `dist` folder.

## Project Structure

```bash
src/
├── components/      # Reusable Vue components
├── views/          # Page components
├── router/         # Vue Router configuration
├── stores/         # Pinia state management
├── services/       # API and utility services
├── App.vue         # Root component
├── main.ts         # Application entry point
└── style.scss      # Global styles
```

## API Integration

The frontend communicates with the backend API at `/api`. The development server includes a proxy that forwards requests to `http://localhost:8000`.

### Authentication

The app uses JWT token-based authentication:

1. User logs in at `/login`
2. Token is stored in localStorage
3. Token is sent in the `Authorization: Bearer {token}` header for all requests

### State Management

Pinia is used for state management with two main stores:

- **AuthStore** - Handles user authentication and authorization
- **ChatStore** - Manages chat messages, threads, and conversation state

## Styling

The frontend uses SCSS for styling with:

- CSS Grid and Flexbox for layouts
- CSS custom properties for theming
- Utility classes for common patterns
- Responsive breakpoints for mobile support

## Components

### Views

- **LoginView** - User authentication
- **ChatView** - Main chat interface with thread management
- **MemoryView** - Memory visualization and management
- **DocumentsView** - Document upload and management
- **ToolsView** - Tool integration control panel

### Stores

- **useAuthStore** - Authentication state and methods
- **useChatStore** - Chat messages and thread management

## Configuration

### Vite Config

Configured in `vite.config.ts`:

- Vue 3 plugin support
- Path alias resolution (@)
- Development API proxy

### TypeScript

Strict mode enabled with Vue support in `tsconfig.json`

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Development Tips

### Adding New Pages

1. Create a new component in `src/views/`
2. Add route in `src/router/index.ts`
3. Link in the navigation bar

### Adding New Stores

1. Create new store in `src/stores/`
2. Use `defineStore('name', () => { ... })`
3. Import and use with `useStore()`

### API Calls

Import the api service and use it:

```typescript
import axios from '@/services/api'

const response = await axios.get('/endpoint')
```

## Troubleshooting

### CORS Issues

Make sure the development server proxy is configured correctly in `vite.config.ts`

### Authentication Failures

Check that the backend is running on port 8000 and the token is being sent correctly

### Build Errors

Run `npm install` to ensure all dependencies are installed

## License

MIT
