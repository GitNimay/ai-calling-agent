# 🚀 Deploying AI Calling Agent to Render

Complete guide to deploy your AI calling agent to Render for free.

---

## ✅ Prerequisites

1. **Render Account** - Sign up at https://render.com (free tier available)
2. **GitHub Account** - Your code must be in a GitHub repository
3. **Gemini API Key** - From https://aistudio.google.com/app/apikey

---

## 📦 Step 1: Push Code to GitHub

```bash
cd "d:\nimesh-portfolio\ai calling agent"

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - AI Calling Agent"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/ai-calling-agent.git
git branch -M main
git push -u origin main
```

---

## 🌐 Step 2: Deploy to Render

### **Option A: Auto Deploy (Recommended)**

1. Go to https://render.com/
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Render will auto-detect the `render.yaml` file
5. Click **"Apply"**

### **Option B: Manual Setup**

1. Go to https://render.com/
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name:** `ai-calling-agent`
   - **Runtime:** `Python 3`
   - **Build Command:** `./build.sh`
   - **Start Command:** `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** `Free`

---

## 🔐 Step 3: Set Environment Variables

In Render dashboard → Environment:

```
GEMINI_API_KEY=AIzaSyCIVswjMgSjlsOBhZRGiTU5Tk79DA7B8m0
GEMINI_MODEL_TEXT=gemini-2.5-flash
GEMINI_MODEL_LIVE=gemini-2.5-flash
PORT=8000
HOST=0.0.0.0
RELOAD=false
```

**Important:**
- ✅ Set `RELOAD=false` for production
- ✅ Add your actual Gemini API key
- ✅ Optional: Add Twilio credentials if using phone calls

---

## 🚀 Step 4: Deploy!

1. Click **"Create Web Service"**
2. Wait 5-10 minutes for build
3. Your app will be live at: `https://your-app-name.onrender.com`

---

## ✅ Step 5: Verify Deployment

Test your endpoints:

```bash
# Health check
curl https://your-app-name.onrender.com/health

# API docs
https://your-app-name.onrender.com/docs
```

---

## 📞 Step 6: Connect Twilio (Optional)

Once deployed, configure Twilio:

1. Go to your Twilio Console
2. Select your phone number
3. Under "Voice & Fax":
   - **A CALL COMES IN:** Webhook
   - **URL:** `https://your-app-name.onrender.com/twilio/incoming`
   - **HTTP:** POST
4. Save

**Now call your Twilio number to talk to the AI!**

---

## 🔧 Troubleshooting

### Build Fails?
- Check logs in Render dashboard
- Ensure `build.sh` has execute permissions: `chmod +x build.sh`
- Verify Python version in `runtime.txt`

### App Crashes?
- Check environment variables are set correctly
- View logs in Render dashboard
- Ensure `GEMINI_API_KEY` is valid

### Slow Performance?
- Free tier has limitations
- Consider upgrading to paid tier for better performance
- Use `RELOAD=false` in production

---

## 💡 Pro Tips

1. **Auto-Deploy:** Enable auto-deploy on GitHub push in Render settings
2. **Custom Domain:** Add your own domain in Render settings
3. **HTTPS:** Render provides free SSL certificates
4. **Monitoring:** Check logs regularly in Render dashboard
5. **Scaling:** Upgrade to paid tier when you need more resources

---

## 🎉 Success!

Your AI calling agent is now:
- ✅ Live on the internet
- ✅ Accessible via public URL
- ✅ Ready for phone calls via Twilio
- ✅ Running 24/7 on Render

**Next Steps:**
- Test the `/chat` endpoint
- Call your Twilio number
- Share the API docs URL
- Monitor usage and logs

---

## 📊 Free Tier Limits

Render Free Tier includes:
- ✅ 750 hours/month (enough for 24/7)
- ✅ Auto-sleep after 15 min inactivity
- ✅ Free SSL/HTTPS
- ⚠️ Spins down after inactivity (first request takes ~30s)

For production, consider the paid tier ($7/month) for:
- No sleep/spin-down
- Better performance
- More resources

---

**Need Help?** Check Render docs: https://render.com/docs
