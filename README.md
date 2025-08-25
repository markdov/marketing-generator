# Jim's Marketing Generator - Deployment Guide

A Flask-based marketing content generator that creates personalized proposals using Google Gemini AI with comprehensive company research.

## 🚀 Quick Deployment to Render.com (Recommended)

### Step 1: Prepare Your Repository
1. Push your code to GitHub (make sure `.env` is not included - use `.env.example` instead)
2. Get your Google Gemini API key ready

### Step 2: Deploy to Render.com
1. Go to [render.com](https://render.com) and sign up/login
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Render will auto-detect your `render.yaml` configuration
5. Set environment variables:
   - `GEMINI_API_KEY`: Your Google Gemini API key

### Step 3: Access Your App
- Your app will be available at: `https://your-app-name.onrender.com`
- Share this URL with your coworkers

## 🔧 Environment Variables Required

Create these in your deployment platform:

```
GEMINI_API_KEY=your_actual_gemini_api_key_here
FLASK_ENV=production
FLASK_DEBUG=False
```

## 💡 Alternative Deployment Options

### Option 2: Railway.app
1. Go to [railway.app](https://railway.app)
2. Connect GitHub repository
3. Add environment variables
4. Deploy automatically

### Option 3: Heroku
1. Install Heroku CLI
2. `heroku create your-app-name`
3. `heroku config:set GEMINI_API_KEY=your_key`
4. `git push heroku main`

## 🔒 Security Notes
- Never commit `.env` files with real API keys
- Use environment variables for all sensitive data
- The app uses HTTPS automatically on Render/Railway/Heroku

## 📋 Features
- Company research and analysis
- AI-powered content generation
- Professional Word document export
- Responsive dark theme UI
- Real-time progress tracking

## 🛠️ Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env_example.txt .env
# Edit .env with your actual API key

# Run locally
python app.py
```

## 📞 Support
If you encounter issues during deployment, check:
1. Environment variables are set correctly
2. Your Gemini API key is valid and has credits
3. All required files are in your repository