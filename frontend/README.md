# Danya's Chess Positions Explorer

An interactive web application for exploring chess positions from Daniel Naroditsky's YouTube speedrun games.

## Features

- 🎯 **Interactive Chess Board** - Play through positions with drag-and-drop functionality
- 📊 **Move Database** - See what moves Danya played and what opponents played in each position
- 🎥 **YouTube Integration** - Direct links to YouTube videos with timestamps for each position
- 📜 **Move History** - Navigate back and forth through your move sequence
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile devices

## Local Development

To run this application locally:

1. Make sure you have the `chess_positions.json` file in the `frontend` directory

2. Start a local web server (required for loading JSON):

   **Option 1: Using Python**
   ```bash
   cd frontend
   python -m http.server 8000
   ```

   **Option 2: Using Node.js (http-server)**
   ```bash
   npm install -g http-server
   cd frontend
   http-server -p 8000
   ```

   **Option 3: Using VS Code Live Server Extension**
   - Install the "Live Server" extension
   - Right-click on `index.html` and select "Open with Live Server"

3. Open your browser and navigate to `http://localhost:8000`

## Deploying to GitHub Pages

### Step 1: Prepare Your Repository

1. Ensure all files are in the `frontend` directory:
   ```
   frontend/
   ├── index.html
   ├── css/
   │   └── styles.css
   ├── js/
   │   └── app.js
   └── chess_positions.json
   ```

2. Commit your changes:
   ```bash
   git add frontend/
   git commit -m "Add chess positions explorer frontend"
   git push origin main
   ```

### Step 2: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click on **Settings** (gear icon)
3. Scroll down to the **Pages** section (in the left sidebar under "Code and automation")
4. Under **Source**, select:
   - Source: `Deploy from a branch`
   - Branch: `main`
   - Folder: `/frontend` (or root if you move files there)
5. Click **Save**

### Step 3: Wait for Deployment

- GitHub will automatically build and deploy your site
- This usually takes 1-2 minutes
- Once complete, you'll see a message: "Your site is live at https://[username].github.io/chess-memory/"

### Step 4: Access Your Site

Your site will be available at:
```
https://[your-github-username].github.io/chess-memory/
```

## Customization Options

### Using a Custom Domain

1. Purchase a domain from a domain registrar
2. In your repo settings under Pages, add your custom domain
3. Configure DNS records with your domain provider:
   - Add a CNAME record pointing to `[username].github.io`
4. Enable HTTPS (automatic with GitHub Pages)

### Performance Optimization

The `chess_positions.json` file is large (~50MB). To optimize:

1. **Enable Gzip Compression** (automatic on GitHub Pages)
2. **Browser Caching** - Add a `.nojekyll` file to the frontend directory
3. **Consider Splitting Data** - If load times are slow, split JSON into chunks

## File Structure

```
frontend/
├── index.html              # Main HTML page
├── css/
│   └── styles.css          # All styling
├── js/
│   └── app.js              # Application logic
├── chess_positions.json    # Position database
└── README.md               # This file
```

## Technologies Used

- **Chessboard.js** - Interactive chess board UI
- **Chess.js** - Chess move validation and game logic
- **jQuery** - Required by Chessboard.js
- **Vanilla JavaScript** - Application logic
- **CSS Grid & Flexbox** - Responsive layout

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Troubleshooting

### JSON File Not Loading
- **Issue**: "Failed to load chess positions"
- **Solution**: Make sure you're running a web server (not opening `file://` directly)
- GitHub Pages automatically serves files correctly

### Board Not Displaying
- **Issue**: Chess board doesn't appear
- **Solution**: Check browser console for errors, ensure CDN links are loading

### Slow Initial Load
- **Issue**: Takes long time to load first time
- **Solution**: Normal for large JSON file (~50MB). Browser will cache it after first load.

### Moves Not Working
- **Issue**: Clicking moves doesn't navigate to new position
- **Solution**: Check console for errors. Position may not exist in database.

## Contributing

Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## License

This project is for educational and personal use.

## Acknowledgments

- Chess position data from Daniel Naroditsky's YouTube speedrun series
- Built with love for the chess community

