# Deployment Guide

This guide covers various deployment options for the Personal Codex Agent.

## 🚀 Quick Deployment Options

### 1. Local Development

```bash
# Clone and setup
git clone <your-repo>
cd personal-codex-agent
chmod +x run.sh
./run.sh
```

### 2. Streamlit Cloud

1. Push code to GitHub
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Add `OPENAI_API_KEY` in secrets
4. Deploy from main branch

**Secrets format** (Streamlit Cloud):
```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "your-key-here"
```

### 3. Replit

1. Import from GitHub to Replit
2. Add `OPENAI_API_KEY` to environment variables
3. Set run command: `streamlit run app.py --server.port 8080`
4. Click Run

### 4. Vercel (with Python runtime)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --env OPENAI_API_KEY=your-key-here
```

**vercel.json**:
```json
{
  "functions": {
    "app.py": {
      "runtime": "@vercel/python"
    }
  },
  "routes": [
    { "src": "/(.*)", "dest": "app.py" }
  ]
}
```

### 5. Docker Deployment

```bash
# Build and run
docker-compose up --build

# Or manually
docker build -t personal-codex-agent .
docker run -e OPENAI_API_KEY=your-key -p 8501:8501 personal-codex-agent
```

### 6. Heroku

```bash
# Install Heroku CLI and login
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your-key-here
git push heroku main
```

**Procfile**:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

## 🔧 Platform-Specific Configuration

### Streamlit Cloud
- Automatic requirements.txt detection
- Environment variables via secrets
- Automatic GitHub integration
- Free tier available

### Replit
- Built-in package management
- Environment variables in sidebar
- Collaborative editing
- Always-on with paid plans

### Vercel
- Serverless deployment
- Automatic scaling
- CDN included
- May have function timeout limits

### Heroku
- Full server environment
- Add-ons available
- Automatic SSL
- Dyno sleep on free tier

## 📊 Performance Considerations

### Resource Requirements
- **RAM**: 512MB minimum, 1GB recommended
- **CPU**: Single core sufficient for demo
- **Storage**: Ephemeral (documents not persisted)
- **Network**: OpenAI API calls required

### Scaling Considerations
- **Document Size**: Current limit ~10MB per file
- **Concurrent Users**: Single user per session
- **API Limits**: OpenAI rate limits apply
- **Memory Usage**: FAISS index in memory

## 🔒 Security Setup

### Environment Variables
```bash
# Required
OPENAI_API_KEY=sk-...

# Optional overrides
OPENAI_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-3-small
```

### Security Best Practices
- Never commit `.env` files
- Use platform secrets management
- Rotate API keys regularly
- Monitor API usage
- Implement rate limiting for production

## 🐛 Troubleshooting

### Common Issues

**"No module named 'src'"**
```bash
# Ensure you're in the project root
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

**"OpenAI API key not found"**
```bash
# Check environment variable
echo $OPENAI_API_KEY
# Or verify .env file exists and has correct format
```

**"Memory error with large documents"**
- Reduce chunk size in config
- Split large documents
- Consider upgrading hosting plan

**"Streamlit not starting"**
```bash
# Try specifying Python version
python3 -m streamlit run app.py
```

### Performance Issues

**Slow document processing**
- Check document size (<10MB recommended)
- Verify OpenAI API response times
- Consider local embedding models

**High memory usage**
- Reduce number of documents
- Implement document cleanup
- Use disk-based vector storage

## 📈 Production Readiness

### Current Limitations
- No user authentication
- No conversation persistence
- Single-session architecture
- In-memory storage only

### Production Enhancements Needed
1. **User Management**
   - Authentication system
   - User-specific document stores
   - Session management

2. **Data Persistence**
   - Database integration
   - Document version control
   - Conversation history

3. **Monitoring**
   - Error tracking
   - Performance metrics
   - API usage monitoring

4. **Scalability**
   - Database-backed vector store
   - Caching layer
   - Load balancing

## 🔮 Next Steps

For production deployment, consider:

1. **Database Integration**
   ```python
   # Replace FAISS with persistent vector DB
   # - Pinecone
   # - Weaviate  
   # - Qdrant
   ```

2. **Advanced Features**
   ```python
   # Add user management
   # Add conversation memory
   # Add document versioning
   # Add analytics dashboard
   ```

3. **Infrastructure**
   ```yaml
   # Kubernetes deployment
   # Auto-scaling
   # Health checks
   # Monitoring stack
   ```

Choose the deployment method that best fits your needs and technical requirements!