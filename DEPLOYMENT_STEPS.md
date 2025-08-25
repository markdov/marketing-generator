# 🚀 Simple Deployment Steps

## Before You Start
1. **Make sure you have a Gemini API key** [[memory:6869800]]
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create an API key
   - Keep it handy for step 4

## Step-by-Step Deployment (5 minutes)

### 1. Push to GitHub
```bash
# If you haven't already:
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/marketing-generator.git
git push -u origin main
```

### 2. Go to Render.com
- Visit [render.com](https://render.com)
- Sign up with GitHub (free account)
- Click **"New +"** → **"Web Service"**

### 3. Connect Your Repository
- Connect your GitHub account
- Select your marketing generator repository
- Render will automatically detect the `render.yaml` file

### 4. Set Environment Variables
In Render dashboard:
- Find **"Environment Variables"** section
- Add: `GEMINI_API_KEY` = `your_actual_api_key_here`
- Other variables are set automatically by render.yaml

### 5. Deploy
- Click **"Create Web Service"**
- Wait 2-3 minutes for deployment
- Your app will be live at: `https://your-app-name.onrender.com`

## 🎉 That's It!

### Share with Your Team
- Send them the URL: `https://your-app-name.onrender.com`
- They can immediately start generating marketing content
- No installation required on their computers

### Free Tier Limitations
- App may sleep after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- Perfect for team use during business hours

## 🔧 If You Need Changes
1. Make changes to your code locally
2. Push to GitHub: `git push`
3. Render automatically redeploys in 1-2 minutes

## 🆘 Troubleshooting

**App won't start?**
- Check that `GEMINI_API_KEY` is set correctly
- Verify your API key works at [Google AI Studio](https://makersuite.google.com/)

**Slow to load?**
- Free tier apps sleep when inactive
- Consider upgrading to $7/month for always-on service

**Need help?**
- Check the Render dashboard logs
- All error messages will appear there
