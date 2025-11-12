# Danya's Chess Positions Explorer

An interactive web application for exploring chess positions from Daniel Naroditsky's YouTube speedrun games.

## Features

- 🎯 **Interactive Chess Board** - Play through positions with drag-and-drop functionality
- 📊 **Move Database** - See what moves Danya played and what opponents played in each position
- 🎥 **YouTube Integration** - Direct links to YouTube videos with timestamps for each position
- 📜 **Move History** - Jump backward or forward and branch new variations at any point
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile devices

## Local Development

An included helper script, `serve.py`, runs a lightweight web server with clean URLs:

```bash
cd frontend
python serve.py
```

The server starts at `http://localhost:8000/`. Press `Ctrl+C` to stop.

If you prefer other options, any static file server works (e.g., `python -m http.server 8000` or `http-server -p 8000`), as long as you serve from the `frontend` directory so the JSON file can be fetched over HTTP.

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

### Debug Logging
- **Enable**: Set `DEBUG_ENABLED = true` near the top of `js/app.js`
- **Disable**: Leave `DEBUG_ENABLED` as `false` for normal usage
- When enabled, the browser console outputs detailed state transitions and history operations.

## Supporting the Project

Hosting the explorer costs about **$10 per month**.  
Donations go solely toward paying for hosting and bandwidth. Any excess will be donated to the Charlotte Chess Center:

- Donation link: [buymeacoffee.com/micshafes](https://buymeacoffee.com/micshafes)


## Contributing

Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## License

The frontend code is released under the [MIT License](../LICENSE). Chess game data and YouTube content remain the property of their respective owners.

## Acknowledgments

- Chess position data from Daniel Naroditsky's YouTube speedrun series
- Built with love for the chess community

