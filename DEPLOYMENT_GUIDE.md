# Deployment Guide: Basis Set Visualizer to Streamlit Community Cloud

## What This Will Do

After following these steps, your app will be:
- ✅ Publicly accessible at a URL like `https://basis-set-viewer.streamlit.app`
- ✅ Available to anyone in the world
- ✅ Automatically updated when you push changes to GitHub
- ✅ Hosted for FREE on Streamlit Community Cloud

---

## Prerequisites

✅ Your app is already working locally (you've tested it)
✅ Code is on GitHub at: https://github.com/Indranil2020/DFT_visual
✅ All files are committed and pushed

---

## Step-by-Step Deployment Instructions

### STEP 1: Go to Streamlit Community Cloud

1. Open your browser and go to: **https://share.streamlit.io/**
   - OR: **https://streamlit.io/cloud**

2. Click the **"Sign up"** or **"Sign in with GitHub"** button

3. Authorize Streamlit to access your GitHub account
   - This is safe - Streamlit is the official hosting platform from the creators of Streamlit
   - It needs access to read your repositories

---

### STEP 2: Create New App

1. Once logged in, click **"New app"** button (top right)

2. You'll see a form with three fields:

   **Repository:** `Indranil2020/DFT_visual`
   - Start typing and it will autocomplete from your GitHub repos

   **Branch:** `main`
   - Should be automatically selected

   **Main file path:** `basis_visualizer_app.py`
   - Type this exactly as shown

3. **Advanced settings** (click to expand - OPTIONAL):
   - **App URL**: You can customize this (e.g., `basis-set-viewer`)
   - **Python version**: Leave as default (3.9 or higher)
   - **Secrets**: Not needed for this app

4. Click **"Deploy!"** button

---

### STEP 3: Wait for Deployment (2-5 minutes)

You'll see a deployment log showing:
```
[2025-11-19 04:00:00] Starting up...
[2025-11-19 04:00:15] Cloning repository...
[2025-11-19 04:00:30] Installing dependencies from requirements.txt...
[2025-11-19 04:02:00] Starting Streamlit app...
[2025-11-19 04:02:30] App is live! 🎉
```

**What's happening:**
- Streamlit is cloning your GitHub repo
- Installing all packages from `requirements.txt`
- Starting your app on their servers
- Giving you a public URL

---

### STEP 4: Get Your Public URL

Once deployed, you'll see:
- ✅ **Your app is live at:** `https://[your-app-name].streamlit.app`
- Example: `https://basis-set-viewer.streamlit.app`

**COPY THIS URL** - you'll need it for the next step!

---

### STEP 5: Test Your Deployed App

1. Click the URL or open it in a new tab
2. Verify the app loads correctly
3. Test the periodic table interaction
4. Try visualizing a basis set (e.g., select Hydrogen, basis set "6-31G")
5. Check the 3D visualization works

If everything works: **SUCCESS!** Your tool is now globally accessible! 🎉

---

### STEP 6: Update Your Personal Website

Now we need to link this app from your main website:

1. Open a terminal and navigate to your website repo:
   ```bash
   cd ~/git/Indranil2020.github.io
   ```

2. I'll help you update the file to replace the "Coming Soon" button with your actual deployment URL

3. The file to update: `tools/basis-set-viewer.html`
   - Change line 257-259 from:
     ```html
     <a href="#" class="btn btn-secondary" onclick="alert('Streamlit deployment in progress!');">
         <i class="fas fa-rocket"></i> Launch Application (Coming Soon)
     </a>
     ```

   - To:
     ```html
     <a href="https://YOUR-APP-URL.streamlit.app" class="btn btn-primary" target="_blank">
         <i class="fas fa-rocket"></i> Launch Application
     </a>
     ```

4. Commit and push:
   ```bash
   git add tools/basis-set-viewer.html
   git commit -m "Add Basis Set Visualizer deployment URL"
   git push origin main
   ```

5. Wait 1-2 minutes for GitHub Pages to update

6. Visit: `https://indranil2020.github.io/tools/basis-set-viewer.html`

**Now anyone can click "Launch Application" and use your tool!**

---

## How Auto-Updates Work

**Future updates are automatic!**

Whenever you push changes to your GitHub repository:
```bash
cd ~/git/DFT_TOOLS
# Make changes to basis_visualizer_app.py
git add .
git commit -m "Improved visualization"
git push origin main
```

Streamlit Community Cloud will:
- Detect the changes automatically
- Rebuild your app
- Deploy the new version
- **No manual redeployment needed!**

---

## Monitoring Your App

### Streamlit Dashboard

Access at: https://share.streamlit.io/

You can:
- ✅ See app status (running, stopped, error)
- ✅ View logs and errors
- ✅ Check resource usage
- ✅ See visitor analytics
- ✅ Restart the app if needed
- ✅ Delete or rename the app

### Free Tier Limits

Streamlit Community Cloud is free with:
- ✅ Unlimited apps
- ✅ 1 GB RAM per app (plenty for this app)
- ✅ Unlimited visitors
- ✅ Auto-sleep after 7 days of no activity (wakes up instantly when someone visits)

---

## Troubleshooting

### Problem: "Module not found" error

**Solution:** Missing dependency in `requirements.txt`

1. Check the error log in Streamlit dashboard
2. Add the missing package to `requirements.txt`
3. Push to GitHub - app will auto-redeploy

---

### Problem: App crashes with memory error

**Solution:** The basis set caching might be too aggressive

Current `requirements.txt` should be fine, but if issues occur:
- Reduce cache size in the app
- Contact me to optimize caching

---

### Problem: App is slow to load

**Solution:** This is normal for first load
- Streamlit apps "sleep" after inactivity
- First visitor wakes it up (takes ~30 seconds)
- After that, it's instant for everyone

---

### Problem: App doesn't update after pushing changes

**Solution:**
1. Go to https://share.streamlit.io/
2. Find your app
3. Click "Reboot app"
4. Wait 1-2 minutes

---

## Sharing Your Tool

Once deployed, share it with:

### Academic Networks
- Add to your Google Scholar profile
- Share on ResearchGate
- Post on LinkedIn: "Excited to release a free web tool for basis set visualization!"
- Tweet with hashtags: #ComputationalChemistry #DFT #OpenScience

### Email Signature
```
Indranil Mal
P4F Fellow, Institute of Physics, Czech Academy of Sciences

🌐 Website: https://indranil2020.github.io
🔬 Basis Set Visualizer: https://[your-app].streamlit.app
```

### Conferences & Papers
- Include the URL in your presentations
- Add to computational chemistry papers as a supplementary tool
- Mention in acknowledgments if others use it for their research

---

## Cost & Sustainability

**Completely FREE!**
- No credit card required
- No hidden fees
- Unlimited usage
- Backed by Streamlit (owned by Snowflake)

**Sustainable long-term:**
- Streamlit Community Cloud is designed for open-source projects
- They want to support scientific and educational tools
- Your app aligns perfectly with their mission

---

## Next Steps After Deployment

1. **Monitor usage** via Streamlit dashboard
2. **Gather feedback** from users
3. **Improve features** based on feedback
4. **Add the k.p model calculator** as a second tool (follow the same process)
5. **Write a blog post** about the tool on your website
6. **Submit to** computational chemistry tool directories

---

## Need Help?

**Streamlit Documentation:**
- https://docs.streamlit.io/streamlit-community-cloud

**Streamlit Community Forum:**
- https://discuss.streamlit.io/

**Contact me if you encounter issues during deployment**

---

## Summary

**What you need to do:**
1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. Click "New app"
4. Select: `Indranil2020/DFT_visual` + `basis_visualizer_app.py`
5. Click "Deploy"
6. Copy the URL you get
7. Tell me the URL so I can update your website

**Time required:** 5-10 minutes
**Result:** Globally accessible scientific tool! 🎉
