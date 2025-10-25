# Contributing to Danya's Chess Positions Explorer

Thank you for your interest in contributing! This project is a labor of love for the chess community, and we welcome contributions of all kinds.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Project Areas](#project-areas)

## 🤝 Code of Conduct

This project is dedicated to Daniel Naroditsky's educational legacy. Please be:
- **Respectful** - to all contributors and users
- **Constructive** - provide helpful feedback
- **Patient** - we're all learning
- **Collaborative** - work together toward common goals

## 💡 How Can I Contribute?

### Reporting Bugs
Found a bug? Please open an issue with:
- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Screenshots (if applicable)
- Browser/OS information

### Suggesting Features
Have an idea? Open an issue with:
- Clear description of the feature
- Use cases and benefits
- Mockups or examples (if applicable)
- Willingness to implement it yourself

### Improving Documentation
- Fix typos or unclear explanations
- Add examples or clarifications
- Translate documentation
- Create tutorials or guides

### Contributing Code
- Fix bugs
- Implement features
- Improve performance
- Refactor code
- Add tests

## 🚀 Getting Started

### Prerequisites

**Frontend Development**:
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Text editor or IDE (VS Code recommended)
- Basic knowledge of HTML, CSS, JavaScript

**Backend Development**:
- Python 3.8 or higher
- pip (Python package manager)
- Basic knowledge of Python
- Understanding of chess notation (helpful but not required)

### Setup

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then:
   git clone https://github.com/YOUR_USERNAME/chess-gift.git
   cd chess-gift
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Set up development environment**
   
   **For Frontend**:
   ```bash
   cd frontend
   python -m http.server 8000
   # Open http://localhost:8000 in your browser
   ```
   
   **For Backend**:
   ```bash
   cd backend/scripts
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Make your changes**
   - Write clean, well-commented code
   - Follow existing code style
   - Test your changes

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Type: Brief description
   
   Detailed explanation of what changed and why."
   ```

6. **Push and create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   # Then create PR on GitHub
   ```

## 🔄 Development Workflow

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `perf/description` - Performance improvements
- `test/description` - Test additions/fixes

### Commit Messages

Follow this format:
```
Type: Brief summary (50 chars or less)

Detailed explanation (if needed):
- What changed
- Why it changed
- Any breaking changes or important notes

Related issues: #123, #456
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples**:
```
feat: Add move highlighting on hover

fix: Resolve board flip bug on mobile devices

docs: Update README with deployment instructions

refactor: Simplify FEN normalization logic
```

### Testing Your Changes

**Frontend**:
```bash
# Test in multiple browsers
# Check console for errors
# Test on mobile/tablet views
# Verify with different positions
```

**Backend**:
```bash
# Run scripts with test data
# Check output files
# Verify database integrity
# Test error handling
```

## 💻 Coding Standards

### Frontend (HTML/CSS/JavaScript)

**HTML**:
- Use semantic HTML5 elements
- Include meaningful comments for sections
- Maintain accessibility standards
- Keep structure clean and organized

**CSS**:
- Use CSS custom properties (variables)
- Group related styles together
- Comment major sections
- Mobile-first responsive design
- Maintain existing naming conventions

**JavaScript**:
- Use clear, descriptive variable names
- Add JSDoc comments for functions
- Handle errors gracefully
- Keep functions focused and small
- Avoid global variables when possible

**Example**:
```javascript
/**
 * Navigate to a specific chess position.
 * Updates board, move list, and video links.
 * 
 * @param {string} fen - FEN notation of target position
 */
function navigateToPosition(fen) {
    addToHistory(fen);
    loadPositionData(fen);
}
```

### Backend (Python)

Follow PEP 8 style guide:
- Use 4 spaces for indentation
- Maximum line length: 88 characters (Black formatter)
- Use descriptive variable names
- Add docstrings to all functions
- Type hints recommended

**Example**:
```python
def extract_video_id(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from various URL formats.
    
    Args:
        url: YouTube URL (youtu.be or youtube.com format)
        
    Returns:
        Video ID string, or None if extraction fails
        
    Examples:
        >>> extract_video_id("https://youtu.be/ABC123?t=42")
        'ABC123'
    """
    # Implementation here
```

### File Organization

**Frontend**:
```
frontend/
├── index.html          # Main structure, well-commented
├── css/
│   └── styles.css      # Organized by section with comments
└── js/
    └── app.js          # Grouped by functionality with section headers
```

**Backend**:
```
backend/scripts/
├── 1_*.py              # Pipeline scripts, numbered in order
├── *.py                # Utility scripts with descriptive names
└── README.md           # Pipeline documentation
```

## 🧪 Testing Guidelines

### Manual Testing Checklist

**Frontend**:
- [ ] Board displays correctly
- [ ] Pieces can be dragged and dropped
- [ ] Move buttons work and update position
- [ ] Video links open to correct timestamps
- [ ] History navigation works
- [ ] Board flip button works
- [ ] Sound toggle works
- [ ] Reset button clears history
- [ ] Responsive on mobile/tablet
- [ ] No console errors

**Backend**:
- [ ] Scripts run without errors
- [ ] Output files are created
- [ ] Database has expected number of positions
- [ ] Video metadata is populated
- [ ] JSON export is valid
- [ ] Progress logging is clear

### Adding Test Data

When contributing features, include test cases:

1. **Small test dataset** in `data/csv/test_games.csv`
2. **Expected output** documented
3. **Edge cases** considered

## 📚 Documentation

### When to Update Documentation

Update docs when you:
- Add new features
- Change existing behavior
- Add new scripts or files
- Modify the data pipeline
- Change setup/installation steps

### Documentation Locations

- `README.md` - Project overview, quick start
- `CONTRIBUTING.md` - This file
- `backend/scripts/README.md` - Pipeline documentation
- `frontend/README.md` - Frontend-specific details
- Code comments - Inline documentation
- Docstrings - Function/class documentation

### Documentation Style

- **Clear** - Easy to understand
- **Complete** - Cover all important details
- **Concise** - No unnecessary words
- **Examples** - Show, don't just tell
- **Updated** - Keep in sync with code

## 📤 Submitting Changes

### Pull Request Process

1. **Update documentation** if needed
2. **Test thoroughly** on your machine
3. **Create pull request** with:
   - Clear title describing the change
   - Description of what changed and why
   - Screenshots (for UI changes)
   - Related issues (if any)

4. **Respond to feedback** from maintainers
5. **Make requested changes** if needed
6. **Wait for approval** and merge

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Performance improvement

## Testing
How did you test this?

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Code follows project style
- [ ] Documentation updated
- [ ] No console errors
- [ ] Tested on multiple browsers (for frontend)
- [ ] Scripts run successfully (for backend)

## Related Issues
Fixes #issue_number
```

## 🎯 Project Areas

### Frontend Development

**Beginner-Friendly**:
- Fix typos or styling issues
- Improve mobile responsiveness
- Add loading indicators
- Enhance error messages

**Intermediate**:
- Add keyboard shortcuts
- Implement search/filter features
- Improve performance
- Add new UI components

**Advanced**:
- Add opening explorer
- Implement analysis board
- Add annotation features
- Create position search

### Backend Development

**Beginner-Friendly**:
- Improve logging
- Add error handling
- Update documentation
- Add data validation

**Intermediate**:
- Optimize database queries
- Add caching
- Improve timestamp accuracy
- Handle edge cases

**Advanced**:
- Add new data sources (e.g., Lichess)
- Implement incremental updates
- Add data verification
- Create automated tests

### Documentation

**Always Welcome**:
- Fix typos
- Clarify confusing sections
- Add examples
- Create tutorials
- Translate to other languages

### Design/UX

- Improve visual design
- Enhance user experience
- Create better layouts
- Design new features
- Improve accessibility

## 🐛 Common Issues & Solutions

### Frontend Issues

**JSON file not loading**:
- Ensure you're using a web server (not `file://`)
- Check browser console for CORS errors
- Verify `chess_positions.json` exists

**Board not displaying**:
- Check CDN links are loading
- Verify no JavaScript errors in console
- Ensure `board` div exists

### Backend Issues

**Chess.com API 403 errors**:
- Add delays between requests
- Check if IP is rate-limited
- Try player archive approach

**Python import errors**:
- Activate virtual environment
- Install requirements: `pip install -r requirements.txt`
- Check Python version (3.8+)

## 🤔 Questions?

- **Not sure where to start?** Open an issue asking for guidance
- **Stuck on something?** Ask for help in your PR
- **Have an idea?** Discuss it in an issue first

## 📜 License Note

By contributing, you agree that your contributions will be licensed under the same terms as the project (educational use).

---

## 🙏 Thank You!

Every contribution, no matter how small, helps make this project better for chess students everywhere. Your efforts honor Daniel Naroditsky's legacy of chess education.

**Happy contributing! ♟️**

