# Quick Start Guide

Get your Chess Positions Explorer running in 5 minutes!

## 🚀 Deploy to GitHub Pages (Fastest)

### 1. Push to GitHub (if not already done)

```bash
git add .
git commit -m "Add chess positions explorer"
git push origin main
```

### 2. Enable GitHub Pages

1. Go to: `https://github.com/YOUR-USERNAME/chess-memory/settings/pages`
2. Under "Build and deployment":
   - Source: **Deploy from a branch**
   - Branch: **main**
   - Folder: **/frontend**
3. Click **Save**

### 3. Access Your Site

Wait 1-2 minutes, then visit:
```
https://YOUR-USERNAME.github.io/chess-memory/
```

✅ **Done!** Your site is live!

---

## 💻 Test Locally First

### Option 1: Python (Easiest)

```bash
cd frontend
python -m http.server 8000
```

Visit: `http://localhost:8000`

### Option 2: Node.js

```bash
npm install -g http-server
cd frontend
http-server -p 8000
```

Visit: `http://localhost:8000`

### Option 3: VS Code Live Server

1. Install "Live Server" extension
2. Right-click `index.html`
3. Select "Open with Live Server"

---

## ✨ Features to Try

1. **Make a Move** - Drag a piece or click a move button
2. **Navigate History** - Use ◀️ ▶️ buttons
3. **Watch Videos** - Click any YouTube link
4. **Flip Board** - Use 🔄 button
5. **Copy FEN** - Click the FEN input field

---

## 🐛 Troubleshooting

**Problem**: Board doesn't load
- ✅ Make sure you're using a web server (not opening file:// directly)

**Problem**: "Failed to load positions"
- ✅ Check that `chess_positions.json` is in the same folder as `index.html`

**Problem**: Site not updating on GitHub Pages
- ✅ Go to Actions tab and wait for deployment to finish
- ✅ Hard refresh your browser (Ctrl+Shift+R)

---

## 📚 More Help

- Full instructions: See `DEPLOYMENT.md`
- Features & tech: See `README.md`
- Issues: Check browser console (F12)

---

**Enjoy exploring Danya's positions!** 🎯♟️

