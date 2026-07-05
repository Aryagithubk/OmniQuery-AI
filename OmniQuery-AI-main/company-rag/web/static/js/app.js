const form = document.getElementById('query-form');
const input = document.getElementById('query-input');
const chatContainer = document.getElementById('chat-container');
const loader = document.getElementById('loader');
const chatInputArea = document.getElementById('chat-input-area');

// Header DOM
const userControls = document.getElementById('user-controls');
const roleBadge = document.getElementById('role-badge');
const logoutBtn = document.getElementById('logout-btn');

// Initialize app state
function initAuth() {
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');

    if (!token) {
        window.location.href = '/auth';
        return;
    }

    chatContainer.classList.remove('hidden');
    chatInputArea.classList.remove('hidden');
    userControls.classList.remove('hidden');
    roleBadge.textContent = 'Role: ' + role.toUpperCase();
}

// Initial Call
initAuth();


// Logout
logoutBtn.addEventListener('click', () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    window.location.href = '/auth';
});

// Suggestion chips
document.querySelectorAll('.suggestion-chip').forEach(chip => {
    chip.addEventListener('click', () => {
        input.value = chip.textContent;
        form.dispatchEvent(new Event('submit'));
    });
});

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = input.value.trim();
    if (!query) return;

    // Remove welcome message
    const welcome = document.querySelector('.welcome-message');
    if (welcome) welcome.remove();

    // Show user message
    appendMessage(query, 'user');
    input.value = '';
    loader.style.display = 'flex';

    try {
        const token = localStorage.getItem('token');
        const headers = { 'Content-Type': 'application/json' };
        if (token) {
            headers['Authorization'] = 'Bearer ' + token;
        }

        const res = await fetch('/api/v1/query', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({ query })
        });

        if (res.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('token');
            localStorage.removeItem('role');
            window.location.href = '/auth';
            return;
        }

        const data = await res.json();
        appendMessage(
            data.answer,
            'bot',
            data.sources || [],
            data.agents_used || [],
            data.confidence || 0
        );
    } catch (err) {
        console.error('Query error:', err);
        appendMessage('⚠️ Sorry, I couldn\'t reach the server. Please ensure the backend is running on port 8000.', 'bot');
    } finally {
        loader.style.display = 'none';
    }
});

function appendMessage(text, sender, sources = [], agentsUsed = [], confidence = 0) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);

    const avatar = document.createElement('div');
    avatar.classList.add('avatar');
    avatar.textContent = sender === 'user' ? '👤' : '✨';

    const contentDiv = document.createElement('div');
    contentDiv.classList.add('message-content');

    const textDiv = document.createElement('div');
    textDiv.classList.add('text');
    textDiv.innerHTML = formatText(text);
    contentDiv.appendChild(textDiv);

    if (sender === 'bot') {
        // ── Agent badges ──
        if (agentsUsed.length > 0) {
            const agentsDiv = document.createElement('div');
            agentsDiv.classList.add('agents-used');
            agentsDiv.innerHTML = agentsUsed.map(agent => {
                const icon = getAgentIcon(agent);
                const cls = getAgentClass(agent);
                return `<span class="agent-badge ${cls}">${icon} ${agent}</span>`;
            }).join('');

            // Confidence indicator
            if (confidence > 0) {
                const pct = Math.round(confidence * 100);
                const level = confidence >= 0.7 ? 'high' : confidence >= 0.4 ? 'med' : 'low';
                agentsDiv.innerHTML += `<span class="confidence-badge confidence-${level}">${pct}% confidence</span>`;
            }

            contentDiv.appendChild(agentsDiv);
        }

        // ── Source citations ──
        if (sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.classList.add('sources');
            sourcesDiv.innerHTML = 'Sources: ' + sources.map(s => {
                const icon = getSourceIcon(s.source_type);
                const name = getSourceName(s);
                const cls = getSourceClass(s.source_type);
                return `<span class="source-tag ${cls}">${icon} ${name}</span>`;
            }).join('');
            contentDiv.appendChild(sourcesDiv);
        }
    }

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(contentDiv);
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function getAgentIcon(agent) {
    const icons = {
        'DocAgent': '📄',
        'DBAgent': '🗄️',
        'ConfluenceAgent': '📖',
        'WebSearchAgent': '🌐',
        'Fallback': 'ℹ️',
    };
    return icons[agent] || '🤖';
}

function getAgentClass(agent) {
    const classes = {
        'DocAgent': 'agent-doc',
        'DBAgent': 'agent-db',
        'ConfluenceAgent': 'agent-confluence',
        'WebSearchAgent': 'agent-web',
        'Fallback': 'agent-fallback',
    };
    return classes[agent] || '';
}

function getSourceIcon(type) {
    const icons = {
        'document': '📄',
        'database': '🗄️',
        'confluence': '📖',
        'web': '🌐',
        'general_knowledge': 'ℹ️',
    };
    return icons[type] || '📎';
}

function getSourceClass(type) {
    const classes = {
        'document': 'source-doc',
        'database': 'source-db',
        'confluence': 'source-confluence',
        'web': 'source-web',
        'general_knowledge': 'source-general',
    };
    return classes[type] || '';
}

function getSourceName(source) {
    if (source.source_type === 'document') {
        const path = source.source_identifier || 'Unknown';
        return path.split('\\').pop().split('/').pop();
    }
    if (source.source_type === 'database') {
        return source.excerpt || 'Database Query';
    }
    if (source.source_type === 'web') {
        try {
            return new URL(source.source_identifier).hostname;
        } catch {
            return 'Web Source';
        }
    }
    if (source.source_type === 'confluence') {
        return 'Confluence Page';
    }
    return source.source_identifier || 'Unknown';
}

// ────────────────────────────────────────────────
// Text Formatting — Markdown → HTML
// ────────────────────────────────────────────────

function formatText(text) {
    if (!text) return '';

    // Split into lines for processing
    var lines = text.split('\n');
    var result = [];
    var tableLines = [];
    var inTable = false;

    for (var i = 0; i < lines.length; i++) {
        var line = lines[i].trim();
        var isTableRow = line.startsWith('|') && line.endsWith('|');
        var isSeparator = /^\|[\s\-:|]+\|$/.test(line);

        if (isTableRow || isSeparator) {
            if (!inTable) inTable = true;
            tableLines.push(line);
        } else {
            if (inTable) {
                result.push(renderMarkdownTable(tableLines));
                tableLines = [];
                inTable = false;
            }
            // Format non-table lines
            if (line === '') {
                result.push('<br>');
            } else {
                result.push(formatLine(line));
            }
        }
    }
    // Flush remaining table
    if (inTable && tableLines.length > 0) {
        result.push(renderMarkdownTable(tableLines));
    }

    return result.join('\n');
}


function formatLine(line) {
    // 1. First, escape HTML entities for safety
    line = line
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    // 2. Convert markdown links [text](url) → clickable <a> tags
    //    This runs AFTER escaping so we need to handle it carefully
    line = line.replace(/\[([^\]]+)\]\(([^)]+)\)/g, function(match, linkText, url) {
        // Check if it's a PDF report download link
        if (url.indexOf('/static/reports/') !== -1) {
            return '<a href="' + url + '" target="_blank" download class="pdf-download-btn">📥 ' + linkText + '</a>';
        }
        // Check if it's any other downloadable file
        if (url.match(/\.(pdf|csv|xlsx|doc|docx|zip)$/i)) {
            return '<a href="' + url + '" target="_blank" download class="pdf-download-btn">📥 ' + linkText + '</a>';
        }
        // Regular link
        return '<a href="' + url + '" target="_blank" class="inline-link">' + linkText + '</a>';
    });

    // 3. Convert raw URLs that aren't already wrapped in <a> tags
    //    Matches http/https URLs and /static/reports/ paths
    line = line.replace(
        /(?<!href="|">)(?:https?:\/\/[^\s<]+|\/static\/reports\/[\w\-]+\.pdf)/g,
        function(url) {
            if (url.indexOf('/static/reports/') !== -1) {
                return '<a href="' + url + '" target="_blank" download class="pdf-download-btn">📥 Download Report</a>';
            }
            return '<a href="' + url + '" target="_blank" class="inline-link">' + url + '</a>';
        }
    );

    // 4. Markdown formatting
    line = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    line = line.replace(/\*(.*?)\*/g, '<em>$1</em>');
    line = line.replace(/`(.*?)`/g, '<code>$1</code>');

    return line;
}


function renderMarkdownTable(lines) {
    if (lines.length < 2) return lines.join('<br>');

    // Find and remove the separator line (usually index 1)
    var headerLine = lines[0];
    var dataStartIndex = 1;

    // Skip separator line(s)
    for (var s = 1; s < lines.length; s++) {
        if (/^\|[\s\-:|]+\|$/.test(lines[s])) {
            dataStartIndex = s + 1;
            break;
        }
    }

    // Parse header
    var headerCells = headerLine.split('|').filter(function(c) { return c.trim() !== ''; });

    // Build the table HTML
    var html = '<div class="db-table-wrapper">';
    html += '<div class="db-table-header">';
    html += '<span class="db-table-icon">📊</span>';
    html += '<span class="db-table-title">Query Results</span>';
    html += '<span class="db-table-count">' + (lines.length - dataStartIndex) + ' rows</span>';
    html += '</div>';
    html += '<div class="db-table-scroll">';
    html += '<table class="db-result-table">';

    // Header row
    html += '<thead><tr>';
    headerCells.forEach(function(cell, idx) {
        html += '<th>' + cell.trim() + '</th>';
    });
    html += '</tr></thead>';

    // Data rows
    html += '<tbody>';
    for (var i = dataStartIndex; i < lines.length; i++) {
        var cells = lines[i].split('|').filter(function(c) { return c.trim() !== ''; });
        // Skip if it looks like a separator
        if (/^[\s\-:|]+$/.test(cells.join(''))) continue;

        var rowClass = (i - dataStartIndex) % 2 === 0 ? 'even-row' : 'odd-row';
        html += '<tr class="' + rowClass + '">';
        cells.forEach(function(cell, idx) {
            var value = cell.trim();
            // Detect numeric values for right-alignment
            var isNumeric = /^[\d,]+(\.\d+)?$/.test(value);
            var cellClass = isNumeric ? ' class="numeric"' : '';
            html += '<td' + cellClass + '>' + value + '</td>';
        });
        html += '</tr>';
    }
    html += '</tbody></table></div></div>';

    return html;
}
