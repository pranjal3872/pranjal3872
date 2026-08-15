# 🚀 GitHub Profile Setup & Deployment Guide

This guide walks you through publishing your newly created animated profile, self-hosting stats cards, and enabling the contribution snake automation for **pranjal3872**.

---

## 📌 Step 1: Create & Push to Profile Repository

1. Go to GitHub and create a **new repository** named exactly `pranjal3872` (matching your username):
   - Repository name: `pranjal3872`
   - Public: ✅ **Public**
   - Initialize with README: ❌ **No** (we already created `README.md`)

2. Run the following commands in your terminal to initialize git and push:
   ```bash
   cd c:\Users\3872p\Documents\antigravity\cool-carson
   git init
   git branch -M main
   git remote add origin https://github.com/pranjal3872/pranjal3872.git
   git add .
   git commit -m "feat: complete animated github profile setup"
   git push -u origin main
   ```

---

## 🐍 Step 2: Enable Contribution Snake Workflow

1. Go to your repository on GitHub: `https://github.com/pranjal3872/pranjal3872`
2. Click **Settings** ⚙️ → **Actions** → **General**.
3. Under **Workflow permissions**, select **"Read and write permissions"** and click **Save**. *(Note: This is in repository settings, not account settings).*
4. Go to the **Actions** tab on GitHub → Click **Generate Snake Animation** workflow → Click **Run workflow**.
5. Once the Action turns green (completed), the `output` branch will automatically be created containing your snake SVGs!

---

## 📊 Step 3: Self-Host `github-readme-stats` (Avoid API Rate Limits)

Public instances of stats cards frequently hit GitHub rate limits. Follow these 5 steps to host your own free private instance on Vercel:

1. **Create GitHub Classic Token**:
   - Go to GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**.
   - Click **Generate new token (classic)**.
   - Note / Expiration: Select **No expiration**.
   - Select scopes: Check **`repo`** scope.
   - Click **Generate token** and **copy it immediately**! *(Do not paste it publicly).*

2. **Fork Stats Repository**:
   - Visit [`anuraghazra/github-readme-stats`](https://github.com/anuraghazra/github-readme-stats) and click **Fork**.

3. **Deploy on Vercel**:
   - Sign up/Log in to [Vercel](https://vercel.com) using your GitHub account (Hobby Free Plan).
   - Click **Add New Project** → Import your forked `github-readme-stats` repository.

4. **Add Environment Variable**:
   - Under **Environment Variables**, add:
     - **Key**: `PAT_1`
     - **Value**: *(Your copied GitHub token)*
   - Click **Deploy**.

5. **Update README**:
   - Once deployed, copy your Vercel app URL (e.g., `https://your-stats-app.vercel.app`).
   - Replace `https://github-readme-stats.vercel.app` in your `README.md` with your custom Vercel app URL!

---

## 🎨 Asset Summary Created in Workspace:

| File | Description |
| :--- | :--- |
| [`dark.svg`](file:///c:/Users/3872p/Documents/antigravity/cool-carson/dark.svg) | Dark-mode animated dithered terminal banner (1180x610) |
| [`light.svg`](file:///c:/Users/3872p/Documents/antigravity/cool-carson/light.svg) | Light-mode animated dithered terminal banner (1180x610) |
| [`README.md`](file:///c:/Users/3872p/Documents/antigravity/cool-carson/README.md) | Complete GitHub profile Markdown file |
| [`.github/workflows/snake.yml`](file:///c:/Users/3872p/Documents/antigravity/cool-carson/.github/workflows/snake.yml) | 12-hour cron workflow for contribution snake |
| [`build_complete_profile.py`](file:///c:/Users/3872p/Documents/antigravity/cool-carson/build_complete_profile.py) | Python script used for dither segmentation & SVG generation |
