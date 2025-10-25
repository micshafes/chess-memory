# Danya's Chess Positions Explorer

> An interactive web application for exploring chess positions from Daniel Naroditsky's YouTube speedrun games.

![Chess Position Explorer](https://img.shields.io/badge/Chess-Position%20Explorer-success)
![License](https://img.shields.io/badge/license-Educational-blue)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Demo](#demo)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Data Pipeline](#data-pipeline)
- [Contributing](#contributing)
- [Development](#development)
- [Deployment](#deployment)
- [Acknowledgments](#acknowledgments)
- [License](#license)

## 🎯 Overview

This project lets you explore every chess position from Daniel Naroditsky's (Danya's) famous YouTube speedrun series. Search any position to see:

- 🟢 **What moves Danya played** from that position
- 🔴 **What moves opponents tried** against him
- 🎥 **YouTube video links** with timestamps to watch Danya handle that position
- ♟️ **Interactive board** with drag-and-drop move exploration

Perfect for chess students who want to learn from Danya's incredible teaching content in a searchable, interactive format.

## ✨ Features

### Frontend Application
- **Interactive Chess Board** - Drag-and-drop pieces to explore positions
- **Move Database** - See all moves Danya and opponents played from each position
- **YouTube Integration** - Direct links to videos with exact timestamps
- **Move History** - Navigate forward/backward through your exploration
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Sound Effects** - Optional move/capture sounds
- **Board Flipping** - View from either perspective

### Backend Pipeline
- **Automated Data Processing** - Extracts positions from PGN game files
- **YouTube Title Fetching** - Real video titles via oEmbed API
- **Position Normalization** - Smart FEN matching for transpositions
- **Timestamp Calculation** - Precise video timestamps using game clocks
- **SQLite Database** - Efficient storage and querying

## 🎮 Demo

Try it yourself! (Link will be added when deployed)

## 🚀 Quick Start

### For Users

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/chess-memory.git
   cd chess-memory
   ```

2. **Serve the frontend locally**
   ```bash
   cd frontend
   python -m http.server 8000
   ```

3. **Open in browser**
   ```
   http://localhost:8000
   ```

### For Contributors

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed setup instructions.

## 📁 Project Structure

```
chess-memory/
├── frontend/                   # Static web application
│   ├── index.html             # Main HTML file
│   ├── css/
│   │   └── styles.css         # All styling
│   ├── js/
│   │   └── app.js             # Application logic
│   ├── img/                   # Images (tribute photos)
│   └── chess_positions.json   # Position database (50-100MB)
│
├── backend/                    # Data processing pipeline
│   └── scripts/               # Python scripts for building database
│       ├── 1_match_games_csv_to_api.py
│       ├── 2_build_database_from_games.py
│       ├── 3_fetch_youtube_titles.py
│       ├── 4_clean_database.py
│       ├── 5_export_to_frontend_json.py
│       ├── rebuild_all.py     # Master rebuild script
│       └── README.md          # Pipeline documentation
│
└── data/                       # Data files
    ├── csv/                   # Original game lists
    ├── json/                  # Game data and exports
    └── sqlite/                # SQLite database
```

## 🔄 Data Pipeline

The backend processes raw game data through a 5-step pipeline:

```
1. Match CSV → Chess.com API
   ↓
2. Build SQLite Database (extract positions)
   ↓
3. Fetch YouTube Titles
   ↓
4. Clean Invalid Links
   ↓
5. Export to Frontend JSON
```

See [backend/scripts/README.md](backend/scripts/README.md) for detailed pipeline documentation.

### Running the Pipeline

```bash
cd backend/scripts

# Install dependencies
pip install -r requirements.txt

# Full rebuild (recommended)
python rebuild_all.py

# Or run steps individually
python 1_match_games_csv_to_api.py
python 2_build_database_from_games.py
python 3_fetch_youtube_titles.py
python 4_clean_database.py
python 5_export_to_frontend_json.py

# Copy output to frontend
cp ../../data/json/chess_positions_frontend.json ../../frontend/chess_positions.json
```

## 🤝 Contributing

We welcome contributions! Whether it's:
- 🐛 Bug reports
- 💡 Feature suggestions
- 📝 Documentation improvements
- 🎨 UI/UX enhancements
- 🔧 Code contributions

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 💻 Development

### Prerequisites

**Frontend**:
- Modern web browser
- Local web server (Python, Node.js, or VS Code Live Server)

**Backend**:
- Python 3.8+
- pip (Python package manager)

### Local Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/chess-memory.git
   cd chess-memory
   ```

2. **Set up Python environment** (optional but recommended)
   ```bash
   python -m venv chess_env
   source chess_env/bin/activate  # On Windows: chess_env\Scripts\activate
   ```

3. **Install backend dependencies**
   ```bash
   cd backend/scripts
   pip install -r requirements.txt
   ```

4. **Run the frontend**
   ```bash
   cd ../../frontend
   python -m http.server 8000
   ```

### Testing

- **Frontend**: Open browser console and check for JavaScript errors
- **Backend**: Each script includes error handling and progress logging
- **API Testing**: Use `dev_test_chess_api.py` to verify Chess.com API access

## 🌐 Deployment

### GitHub Pages

1. **Enable GitHub Pages** in repository settings
2. **Set source** to `main` branch, `/frontend` folder
3. **Custom domain** (optional): Add `CNAME` file to frontend

See [frontend/DEPLOYMENT.md](frontend/DEPLOYMENT.md) for detailed deployment instructions.

### Other Platforms

The frontend is a static site and can be deployed to:
- **Netlify**: Drag & drop `frontend/` folder
- **Vercel**: Import GitHub repository
- **Any static host**: Upload `frontend/` contents

## 🎓 How It Works

### Position Matching
Every position in Danya's games is extracted and stored with:
- **FEN notation** (position identifier)
- **Move history** (what Danya played, what opponents tried)
- **Video timestamps** (calculated from game clocks)

### Frontend Architecture
- **Single-page application** - No backend server required
- **Client-side search** - Entire database loaded once
- **Instant lookups** - In-memory position matching
- **Browser caching** - Fast subsequent loads

### Key Technologies
- **Frontend**: Vanilla JavaScript, chessboard.js, chess.js
- **Backend**: Python, python-chess, SQLite
- **APIs**: Chess.com public API, YouTube oEmbed API

## 📊 Data Sources

### Game Data
- Chess games from Daniel Naroditsky's Chess.com accounts:
  - `senseidanya`
  - `hebeccararis`
  - `ohmylands`
  - `frankfurtairport`

### Speedrun Series Included
- Back to 3000
- Beginner to Master
- Develop Your Instincts
- Master Class
- Sensei Speedrun
- Top Theory

## 🙏 Acknowledgments

- **Daniel Naroditsky** - For creating incredible educational content and inspiring the chess community
- **Chess.com** - For providing public API access to game data
- **chessboard.js & chess.js** - For excellent open-source chess libraries
- **The Chess Community** - For supporting chess education

This project was created as a tribute to Danya's teaching legacy and to help chess students learn from his games.

## 📜 License

This project is for educational and personal use.

- Game data is from public Chess.com games
- YouTube content belongs to Daniel Naroditsky
- Code is open-source for educational purposes

Please respect intellectual property rights when using or modifying this project.

---

## 📞 Contact

Have questions or suggestions? Feel free to:
- Open an issue on GitHub
- Submit a pull request
- Share your feedback

---

**Made with ♟️ by chess enthusiasts, for chess students everywhere.**

*In loving memory of Daniel Naroditsky - the world's favorite chess teacher.*

