# GitHub Pages Deployment Guide

This guide will walk you through deploying the Chess Positions Explorer to GitHub Pages.

## Prerequisites

- A GitHub account
- Git installed on your computer
- Your repository pushed to GitHub

## Quick Deployment (Easiest Method)

### Step 1: Check Your Files

Make sure your repository structure looks like this:

```
chess-memory/
├── frontend/
│   ├── index.html
│   ├── chess_positions.json
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── app.js
│   ├── .nojekyll
│   └── README.md
├── backend/
├── data/
└── README.md
```

### Step 2: Commit and Push

```bash
# From the root of your project
git add frontend/
git commit -m "Add chess positions explorer frontend"
git push origin main
```

### Step 3: Enable GitHub Pages

1. Go to https://github.com/[your-username]/chess-memory
2. Click the **Settings** tab (⚙️ icon at the top)
3. In the left sidebar, click **Pages** (under "Code and automation")
4. Under **Build and deployment**:
   - **Source**: Select "Deploy from a branch"
   - **Branch**: Select `main`
   - **Folder**: Select `/frontend`
   - Click **Save**

### Step 4: Wait for Deployment

- GitHub will start building your site automatically
- You'll see a blue notification: "GitHub Pages source saved"
- Wait 1-2 minutes for the build to complete
- Refresh the page, and you'll see: "Your site is live at https://[username].github.io/chess-memory/"

### Step 5: Visit Your Site

Click the link or go to:
```
https://[your-username].github.io/chess-memory/
```

🎉 **That's it! Your site is now live!**

## Updating Your Site

Whenever you make changes:

```bash
git add frontend/
git commit -m "Update chess explorer"
git push origin main
```

GitHub Pages will automatically rebuild and redeploy your site (takes 1-2 minutes).

## Alternative: Deploy from Root Directory

If you prefer to have the files in the root of your repository:

### Option A: Move Files to Root

```bash
# Move files from frontend to root
mv frontend/index.html .
mv frontend/css .
mv frontend/js .
mv frontend/chess_positions.json .
mv frontend/.nojekyll .

# Update GitHub Pages settings to use / (root)
```

### Option B: Create docs/ Folder

GitHub Pages can also deploy from a `docs/` folder:

```bash
# Rename frontend to docs
mv frontend docs

# In GitHub Pages settings, select /docs instead of /frontend
```

## Custom Domain Setup (Optional)

If you want to use your own domain (like chess.yourdomain.com):

### Step 1: Purchase a Domain

Buy a domain from:
- Namecheap
- Google Domains
- Cloudflare
- GoDaddy
- etc.

### Step 2: Configure DNS

Add a CNAME record in your domain's DNS settings:

```
Type:  CNAME
Name:  chess (or @ for root domain)
Value: [your-username].github.io
TTL:   3600 (or automatic)
```

### Step 3: Add Custom Domain in GitHub

1. Go to your repository **Settings** → **Pages**
2. Under **Custom domain**, enter your domain: `chess.yourdomain.com`
3. Click **Save**
4. Enable **Enforce HTTPS** (wait a few minutes for certificate)

### Step 4: Wait for DNS Propagation

- DNS changes can take up to 24 hours (usually much faster)
- Check status at: https://www.whatsmydns.net/

## Troubleshooting

### Issue: "404 - File not found"

**Cause**: GitHub Pages is looking in the wrong directory

**Solution**:
1. Check that you selected the correct folder in Pages settings (`/frontend`)
2. Make sure `index.html` exists in that folder
3. Wait 2-3 minutes after changing settings

### Issue: "Failed to load chess_positions.json"

**Cause**: CORS or file path issues

**Solution**:
1. Ensure `chess_positions.json` is in the same directory as `index.html`
2. Check browser console for specific error
3. Make sure `.nojekyll` file exists (prevents Jekyll processing)

### Issue: "Site not updating after push"

**Cause**: GitHub Pages cache

**Solution**:
1. Go to **Actions** tab in your repo
2. Check if the "pages build and deployment" action is running
3. Wait for it to complete (green checkmark)
4. Clear your browser cache (Ctrl+Shift+R or Cmd+Shift+R)

### Issue: "Large file warning"

**Cause**: `chess_positions.json` is large

**Solution**:
- GitHub Pages supports files up to 100MB (you're fine)
- If you get an error, ensure file is < 100MB
- Consider using Git LFS for files > 50MB (not necessary for this project)

### Issue: Page loads but board doesn't appear

**Cause**: CDN resources not loading

**Solution**:
1. Check browser console for errors
2. Ensure you have internet connection (CDN links need to load)
3. Try a different browser

## Performance Tips

### Enable Caching

Create a `_headers` file in your frontend directory:

```
/chess_positions.json
  Cache-Control: public, max-age=31536000, immutable

/*.js
  Cache-Control: public, max-age=86400

/*.css
  Cache-Control: public, max-age=86400
```

Note: GitHub Pages may not respect custom headers. This is more useful for Netlify/Vercel.

### Compress JSON

To make the JSON file smaller:

```bash
# Using Python
python -c "import json; import sys; json.dump(json.load(open('chess_positions.json')), sys.stdout, separators=(',',':'))" > chess_positions.min.json

# Replace the original
mv chess_positions.min.json chess_positions.json
```

### Monitor Usage

GitHub Pages free tier includes:
- ✅ 100GB bandwidth per month
- ✅ Unlimited builds
- ✅ Free HTTPS

This is more than enough for personal projects!

## Verification Checklist

Before going live, verify:

- [ ] All files committed and pushed to GitHub
- [ ] GitHub Pages enabled in repository settings
- [ ] Site builds successfully (check Actions tab)
- [ ] Site loads at your GitHub Pages URL
- [ ] Chess board displays correctly
- [ ] Can make moves and navigate
- [ ] Video links open correctly
- [ ] Mobile responsive (test on phone)

## Need Help?

If you run into issues:

1. Check the browser console for errors (F12)
2. Check GitHub Actions tab for build errors
3. Verify all files are in the correct location
4. Make sure you're using a modern browser

## Success! 🎉

Once deployed, share your site:
- Tweet it to the chess community
- Share with friends
- Post on r/chess

Enjoy exploring Danya's positions!

