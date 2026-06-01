# QUICKSTART.md - Mind-Bus Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites

- Docker & Docker Compose (recommended)
- OR: Python 3.10+ and Node.js 16+
- OpenAI API key (optional, for demo mode)

### Option 1: Docker (Recommended)

```bash
cd deploy
docker-compose up --build
```

Then open:

- **Frontend**: <http://localhost:5173>
- **API**: <http://localhost:8000>
- **API Docs**: <http://localhost:8000/docs>

**Demo Credentials**:

- Username: `admin`
- Password: `password`

### Option 2: Local Development

#### Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Run API
python -m apps.api.main
```

API runs at <http://localhost:8000>

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at <http://localhost:5173>

### 📚 Next Steps

1. **Login**: Use admin/password
2. **Try Chat**: Send a message to the agent
3. **Explore**: Check out Memory, Documents, and Tools sections
4. **Read Docs**: Check SKILL.md, AGENT.md, INTEGRATION.md

### 📋 Key Features

- 💬 **Chat** - Talk to the AI agent
- 🧠 **Memory** - View agent's memories
- 📄 **Documents** - Upload files for RAG
- 🛠️ **Tools** - Control available tools

### 🔧 Useful Commands

```bash
# Start all services
docker-compose -f deploy/docker-compose.yml up

# View logs
docker-compose -f deploy/docker-compose.yml logs -f api

# Access database
docker-compose -f deploy/docker-compose.yml exec postgres psql -U postgres -d ai_agent

# Stop services
docker-compose -f deploy/docker-compose.yml down
```

### 🐛 Troubleshooting

**Port already in use?**

```bash
# Change port in docker-compose.yml or kill process
lsof -i :5173  # Check frontend port
lsof -i :8000  # Check API port
```

**Frontend won't load?**

- Wait 30 seconds for npm dependencies
- Check browser console for errors
- Try <http://localhost:5173> directly

**API connection error?**

- Ensure API is running on port 8000
- Check VITE_API_URL in frontend/.env
- Verify no firewall blocking

### 📖 Documentation

- **SKILL.md** - Technical reference
- **AGENT.md** - Agent architecture
- **INTEGRATION.md** - API integration guide
- **COMPLETION_SUMMARY.md** - What was built
- **frontend/README.md** - Frontend guide

### 🎯 What You Can Do

- ✅ Chat with AI agent
- ✅ Manage conversation history
- ✅ View extracted memories
- ✅ Upload documents
- ✅ Control tools
- ✅ Custom prompt testing

### 💡 Pro Tips

1. Use `/api` prefix for development (Vite proxy)
2. Check browser DevTools → Network tab for API calls
3. JWT token stored in localStorage
4. All data scoped to logged-in user
5. Demo data resets on server restart

### 🔐 Security Notes

- Change demo credentials in production
- Use HTTPS in production
- Store API keys securely
- Enable CORS only for trusted origins
- Use environment variables for secrets

### 📞 Support

For issues:

1. Check logs: `docker-compose logs -f`
2. Read troubleshooting in INTEGRATION.md
3. Review SKILL.md for technical details
4. Check API docs at /docs endpoint

### 🎓 Learn More

1. Start with INTEGRATION.md for architecture
2. Review SKILL.md for code patterns
3. Check AGENT.md for agent system
4. Explore API docs at /docs

---

**Status**: ✅ Ready to Use

**Time to Running**: ~2 minutes (Docker)

**First Chat**: < 30 seconds

Enjoy using Mind-Bus! 🚀
