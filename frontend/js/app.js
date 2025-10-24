// ===========================
// Global State
// ===========================

let positionsData = []; // All positions from JSON
let positionLookup = {}; // Map: FEN -> position data
let currentPosition = null;
let moveHistory = []; // Stack of positions user has navigated through
let historyIndex = -1; // Current position in history
let board = null;
let game = null;

// Sound effects
let soundEnabled = true;
let audioContext = null;
let moveSound = null;
let captureSound = null;

// ===========================
// Initialization
// ===========================

document.addEventListener('DOMContentLoaded', async () => {
    try {
        await loadPositionsData();
        initializeBoard();
        initializeSounds();
        setupEventListeners();
        
        // Start at the beginning position
        const startFEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -';
        navigateToPosition(startFEN);
        
        hideLoading();
    } catch (error) {
        console.error('Initialization error:', error);
        alert('Failed to load chess positions. Please refresh the page.');
    }
});

// ===========================
// Data Loading
// ===========================

async function loadPositionsData() {
    try {
        const response = await fetch('chess_positions.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        positionsData = await response.json();
        console.log(`Loaded ${positionsData.length} positions`);
        
        // Build lookup map for fast access
        positionsData.forEach(pos => {
            positionLookup[pos.fen] = pos;
        });
        
    } catch (error) {
        console.error('Error loading positions:', error);
        throw error;
    }
}

function hideLoading() {
    document.getElementById('loading-screen').style.display = 'none';
    document.getElementById('main-content').style.display = 'grid';
    
    // Ensure board resizes after container is visible
    setTimeout(() => {
        if (board) {
            board.resize();
        }
    }, 100);
}

// ===========================
// Board Initialization
// ===========================

function initializeBoard() {
    const config = {
        draggable: true,
        position: 'start',
        onDragStart: onDragStart,
        onDrop: onDrop,
        onSnapEnd: onSnapEnd,
        pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png'
    };
    
    board = Chessboard('board', config);
    game = new Chess();
    
    // Make board responsive
    window.addEventListener('resize', () => {
        board.resize();
    });
}

// ===========================
// Board Interaction Handlers
// ===========================

function onDragStart(source, piece, position, orientation) {
    // Don't allow moves if game is over
    if (game.game_over()) return false;
    
    // Only pick up pieces for the side to move
    if ((game.turn() === 'w' && piece.search(/^b/) !== -1) ||
        (game.turn() === 'b' && piece.search(/^w/) !== -1)) {
        return false;
    }
}

function onDrop(source, target) {
    // Ensure game state matches the current position in history
    if (currentPosition && historyIndex >= 0) {
        game.load(moveHistory[historyIndex]);
    }
    
    // Try to make the move
    const move = game.move({
        from: source,
        to: target,
        promotion: 'q' // Always promote to queen for simplicity
    });
    
    // Illegal move
    if (move === null) {
        return 'snapback';
    }
    
    // Check if it was a capture
    const isCapture = move.captured !== undefined;
    
    // Move was legal - navigate to the new position
    const newFEN = getFENWithoutMoveNumbers(game.fen());
    
    // Add to history and load position data (even if not in database)
    addToHistory(newFEN);
    loadPositionData(newFEN);
    
    // Play sound
    playMoveSound(isCapture);
}

function onSnapEnd() {
    board.position(game.fen());
}

// ===========================
// Navigation
// ===========================

function navigateToPosition(fen) {
    addToHistory(fen);
    loadPositionData(fen);
}

function addToHistory(fen) {
    // Remove any forward history if we're not at the end (branching from middle of history)
    if (historyIndex < moveHistory.length - 1) {
        console.log(`Branching from position ${historyIndex}, removing ${moveHistory.length - historyIndex - 1} future moves`);
        moveHistory = moveHistory.slice(0, historyIndex + 1);
    }
    
    // Don't add duplicate positions
    if (moveHistory.length > 0 && moveHistory[moveHistory.length - 1] === fen) {
        console.log('Skipping duplicate position');
        return;
    }
    
    moveHistory.push(fen);
    historyIndex = moveHistory.length - 1;
    console.log(`Added to history. Now at position ${historyIndex} of ${moveHistory.length - 1}`);
    updateNavigationButtons();
}

function navigateBack() {
    if (historyIndex > 0) {
        historyIndex--;
        loadPositionData(moveHistory[historyIndex]);
        updateNavigationButtons();
    }
}

function navigateForward() {
    if (historyIndex < moveHistory.length - 1) {
        historyIndex++;
        loadPositionData(moveHistory[historyIndex]);
        updateNavigationButtons();
    }
}

function navigateToStart() {
    // Jump to the first position in history (index 0)
    if (moveHistory.length > 0) {
        historyIndex = 0;
        loadPositionData(moveHistory[0]);
        updateNavigationButtons();
    }
}

function resetBoard() {
    // Clear all history and start fresh
    moveHistory = [];
    historyIndex = -1;
    
    // Reset to starting position
    const startFEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -';
    
    // Reset the game and board
    game.reset();
    board.start();
    
    // Navigate to start position (this will add it to history)
    navigateToPosition(startFEN);
    
    showNotification('Board reset to starting position', 'success');
}

function navigateToHistoryIndex(index) {
    if (index >= 0 && index < moveHistory.length) {
        historyIndex = index;
        loadPositionData(moveHistory[historyIndex]);
        updateNavigationButtons();
    }
}

function updateNavigationButtons() {
    document.getElementById('btn-back').disabled = historyIndex <= 0;
    document.getElementById('btn-forward').disabled = historyIndex >= moveHistory.length - 1;
}

// ===========================
// Position Loading
// ===========================

function loadPositionData(fen) {
    currentPosition = positionLookup[fen];
    
    // If position not in database, create an empty position object
    if (!currentPosition) {
        console.log('Position not in Danya\'s games:', fen);
        currentPosition = {
            fen: fen,
            videos: [],
            next_by_daniel: [],
            next_faced: []
        };
    }
    
    // Update board and game state
    try {
        game.load(fen);
        board.position(fen);
    } catch (error) {
        console.error('Error loading position on board:', error);
        // Try to recover by resetting
        game.reset();
        board.start();
    }
    
    // Update UI
    updatePositionInfo();
    updateMoveButtons();
    updateVideoLinks();
    updateMoveHistory();
}

function updatePositionInfo() {
    const fen = currentPosition.fen;
    document.getElementById('fen-display').value = fen;
    
    // Calculate move number
    const moveNum = historyIndex + 1;
    document.getElementById('move-number').textContent = 
        historyIndex === 0 ? 'Start position' : `Move ${moveNum}`;
    
    // Update video count
    const videoCount = currentPosition.videos ? currentPosition.videos.length : 0;
    document.getElementById('video-count').textContent = videoCount;
}

function updateMoveButtons() {
    const danyaMoves = currentPosition.next_by_daniel || [];
    const opponentMoves = currentPosition.next_faced || [];
    
    // Update Danya's moves
    const danyaContainer = document.getElementById('danya-moves');
    if (danyaMoves.length > 0) {
        danyaContainer.innerHTML = danyaMoves
            .map(move => `<button class="move-btn danya" onclick="makeMove('${escapeHtml(move)}')" 
                          onmouseenter="highlightMove('${escapeHtml(move)}')" 
                          onmouseleave="clearHighlight()">${escapeHtml(move)}</button>`)
            .join('');
    } else {
        danyaContainer.innerHTML = '<p class="no-moves">Danya hasn\'t played this position<br><small>You can still make any legal move</small></p>';
    }
    
    // Update opponent's moves
    const opponentContainer = document.getElementById('opponent-moves');
    if (opponentMoves.length > 0) {
        opponentContainer.innerHTML = opponentMoves
            .map(move => `<button class="move-btn opponent" onclick="makeMove('${escapeHtml(move)}')" 
                          onmouseenter="highlightMove('${escapeHtml(move)}')" 
                          onmouseleave="clearHighlight()">${escapeHtml(move)}</button>`)
            .join('');
    } else {
        opponentContainer.innerHTML = '<p class="no-moves">No opponent moves recorded<br><small>You can still make any legal move</small></p>';
    }
}

function updateVideoLinks() {
    const videos = currentPosition.videos || [];
    const container = document.getElementById('video-links');
    
    if (videos.length > 0) {
        container.innerHTML = videos
            .map((url, index) => createVideoLinkHTML(url, index + 1))
            .join('');
    } else {
        container.innerHTML = '<p class="no-videos">No videos for this position</p>';
    }
}

function createVideoLinkHTML(url, index) {
    // Extract video ID and timestamp from URL
    const videoId = extractVideoId(url);
    const timestamp = extractTimestamp(url);
    
    const timeFormatted = formatTimestamp(timestamp);
    
    // YouTube thumbnail URL (using high quality default)
    const thumbnailUrl = `https://img.youtube.com/vi/${videoId}/mqdefault.jpg`;
    
    return `
        <a href="${url}" target="_blank" class="video-link">
            <div class="video-thumbnail">
                <img src="${thumbnailUrl}" alt="Video thumbnail" loading="lazy">
                <div class="play-overlay">▶</div>
            </div>
            <div class="video-info">
                <div class="video-title">Danya's Speedrun Game #${index}</div>
                <div class="video-time">⏱️ Start at ${timeFormatted}</div>
            </div>
        </a>
    `;
}

function extractVideoId(url) {
    const match = url.match(/youtu\.be\/([^?]+)/);
    return match ? match[1] : '';
}

function extractTimestamp(url) {
    const match = url.match(/[?&]t=(\d+)/);
    return match ? parseInt(match[1]) : 0;
}

function formatTimestamp(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else {
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }
}

function updateMoveHistory() {
    const container = document.getElementById('move-history-list');
    
    if (moveHistory.length <= 1) {
        container.innerHTML = '<span style="color: #7f8c8d; font-style: italic;">Make moves to see history</span>';
        return;
    }
    
    container.innerHTML = moveHistory
        .map((fen, index) => {
            const isCurrent = index === historyIndex;
            const moveNum = index === 0 ? 'Start' : `${index}`;
            return `<button class="history-move ${isCurrent ? 'current' : ''}" 
                            onclick="navigateToHistoryIndex(${index})">${moveNum}</button>`;
        })
        .join('');
}

// ===========================
// Move Execution
// ===========================

function makeMove(moveNotation) {
    try {
        // Ensure game state matches the current position in history
        if (currentPosition && historyIndex >= 0) {
            game.load(moveHistory[historyIndex]);
        }
        
        // Make the move in chess.js
        const move = game.move(moveNotation);
        
        if (!move) {
            console.error('Invalid move:', moveNotation);
            showNotification('Invalid move', 'error');
            return;
        }
        
        // Check if it was a capture
        const isCapture = move.captured !== undefined;
        
        // Get the new position FEN (without move numbers)
        const newFEN = getFENWithoutMoveNumbers(game.fen());
        
        // Add to history and load position data (even if not in database)
        addToHistory(newFEN);
        loadPositionData(newFEN);
        
        // Play sound
        playMoveSound(isCapture);
        
    } catch (error) {
        console.error('Error making move:', error);
        showNotification('Error making move', 'error');
    }
}

// ===========================
// Sound Effects
// ===========================

function initializeSounds() {
    try {
        // Use Lichess open-source sound files
        moveSound = new Audio('https://lichess1.org/assets/sound/standard/Move.mp3');
        captureSound = new Audio('https://lichess1.org/assets/sound/standard/Capture.mp3');
        
        // Preload sounds
        moveSound.load();
        captureSound.load();
        
        // Set volume
        moveSound.volume = 0.5;
        captureSound.volume = 0.5;
    } catch (error) {
        console.log('Could not initialize sounds:', error);
        soundEnabled = false;
    }
}

function playMoveSound(isCapture = false) {
    if (!soundEnabled) return;
    
    try {
        const sound = isCapture ? captureSound : moveSound;
        
        // Reset and play
        sound.currentTime = 0;
        sound.play().catch(e => {
            console.log('Could not play sound:', e);
            // Browsers may block autoplay - that's ok
        });
    } catch (error) {
        console.log('Error playing sound:', error);
    }
}

function toggleSound() {
    soundEnabled = !soundEnabled;
    const btn = document.getElementById('btn-sound');
    
    if (soundEnabled) {
        btn.textContent = '🔊';
        btn.classList.remove('muted');
        btn.title = 'Sound on (click to mute)';
    } else {
        btn.textContent = '🔇';
        btn.classList.add('muted');
        btn.title = 'Sound off (click to unmute)';
    }
}

// ===========================
// Square Highlighting
// ===========================

function highlightMove(moveNotation) {
    // Clear any existing highlights
    clearHighlight();
    
    try {
        // Create a temporary game instance to test the move
        const tempGame = new Chess(game.fen());
        
        // Try to make the move to get details
        const moveResult = tempGame.move(moveNotation);
        
        if (moveResult) {
            // Get source and destination squares
            const fromSquare = moveResult.from;
            const toSquare = moveResult.to;
            
            // Add highlight classes to the squares
            highlightSquare(fromSquare, 'source');
            highlightSquare(toSquare, 'destination');
        }
    } catch (error) {
        console.log('Could not highlight move:', moveNotation, error);
    }
}

function clearHighlight() {
    // Remove all highlight classes from squares
    const highlightedSquares = document.querySelectorAll('.highlight-source, .highlight-destination');
    highlightedSquares.forEach(square => {
        square.classList.remove('highlight-source', 'highlight-destination');
    });
}

function highlightSquare(square, type) {
    // Chessboard.js uses square IDs like "square-e2"
    // But the actual elements have a class .square-55d63
    // We need to find the square by its data attribute or position
    
    // Find all squares and check for the matching square
    const boardElement = document.getElementById('board');
    const squareElements = boardElement.querySelectorAll('.square-55d63');
    
    squareElements.forEach(element => {
        // The square class includes the square name, e.g., "square-55d63 square-e2"
        const classes = element.className;
        if (classes.includes(`square-${square}`)) {
            element.classList.add(`highlight-${type}`);
        }
    });
}

// ===========================
// Utility Functions
// ===========================

function getFENWithoutMoveNumbers(fen) {
    // Remove the halfmove clock and fullmove number from FEN
    // Keep: position, turn, castling, en passant
    const parts = fen.split(' ');
    return parts.slice(0, 4).join(' ');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showNotification(message, type = 'info') {
    // Simple notification - can be enhanced with a toast library
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // You can add a visual notification here if desired
    // For now, we'll just log to console
}

function flipBoard() {
    board.flip();
}

// ===========================
// Event Listeners
// ===========================

function setupEventListeners() {
    document.getElementById('btn-start').addEventListener('click', navigateToStart);
    document.getElementById('btn-back').addEventListener('click', navigateBack);
    document.getElementById('btn-forward').addEventListener('click', navigateForward);
    document.getElementById('btn-reset').addEventListener('click', resetBoard);
    document.getElementById('btn-flip').addEventListener('click', flipBoard);
    document.getElementById('btn-sound').addEventListener('click', toggleSound);
    
    // Allow clicking on FEN to copy it
    document.getElementById('fen-display').addEventListener('click', function() {
        this.select();
        document.execCommand('copy');
        showNotification('FEN copied to clipboard', 'success');
    });
}

// ===========================
// Exports for inline onclick handlers
// ===========================

// Make functions available globally for inline onclick handlers
window.makeMove = makeMove;
window.navigateToHistoryIndex = navigateToHistoryIndex;
window.highlightMove = highlightMove;
window.clearHighlight = clearHighlight;

