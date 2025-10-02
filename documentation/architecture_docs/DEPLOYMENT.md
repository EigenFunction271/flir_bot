# Deployment Guide

## Environment Variables

Create a `.env` file with the following variables:

```env
# Discord Bot Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_discord_server_id_here

# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Google Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Bot Configuration
BOT_PREFIX=!
DEBUG_MODE=True
```

## Render Deployment

### Step 1: Prepare Repository
1. Push your code to GitHub
2. Ensure `render.yaml` is in the root directory
3. Verify all dependencies are in `requirements.txt`

### Step 2: Deploy to Render
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Select the repository and branch

### Step 3: Configure Service
- **Name**: `flir-discord-bot`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python discord_bot.py`

### Step 4: Set Environment Variables
In Render dashboard, go to Environment tab and add:
- `DISCORD_BOT_TOKEN` - Your Discord bot token
- `GROQ_API_KEY` - Your Groq API key
- `GEMINI_API_KEY` - Your Google Gemini API key
- `DISCORD_GUILD_ID` - Your Discord server ID (optional)
- `BOT_PREFIX` - `!`
- `DEBUG_MODE` - `False`

### Step 5: Deploy
1. Click "Create Web Service"
2. Wait for build to complete
3. Check logs for successful startup
4. Test bot functionality in Discord

## Railway Deployment

### Step 1: Create railway.json
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python discord_bot.py",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Step 2: Deploy to Railway
1. Go to [Railway](https://railway.app/)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Set environment variables in Railway dashboard
5. Deploy automatically

## Heroku Deployment

### Step 1: Create Procfile
```
worker: python discord_bot.py
```

### Step 2: Deploy to Heroku
```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set DISCORD_BOT_TOKEN=your_token
heroku config:set GROQ_API_KEY=your_key
heroku config:set GEMINI_API_KEY=your_key

# Deploy
git push heroku main

# Scale worker dyno
heroku ps:scale worker=1
```

## Docker Deployment

### Step 1: Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "discord_bot.py"]
```

### Step 2: Build and Run
```bash
# Build image
docker build -t flir-bot .

# Run container
docker run -d \
  --name flir-bot \
  -e DISCORD_BOT_TOKEN=your_token \
  -e GROQ_API_KEY=your_key \
  -e GEMINI_API_KEY=your_key \
  flir-bot
```

## Monitoring and Maintenance

### Health Checks
- Monitor bot uptime and response times
- Set up alerts for API failures
- Track conversation completion rates

### Logs
- Monitor application logs for errors
- Set up log aggregation (e.g., LogDNA, Papertrail)
- Track API usage and costs

### Scaling
- Monitor concurrent user sessions
- Scale horizontally if needed
- Implement rate limiting for API calls

## Troubleshooting

### Common Deployment Issues

1. **Build Failures**
   - Check Python version compatibility
   - Verify all dependencies in requirements.txt
   - Check for missing environment variables

2. **Runtime Errors**
   - Verify all API keys are set correctly
   - Check Discord bot permissions
   - Monitor API rate limits

3. **Performance Issues**
   - Monitor API response times
   - Implement caching for character responses
   - Optimize conversation history storage

### Support
- Check deployment platform documentation
- Monitor application logs
- Test API connections with `!test` command
