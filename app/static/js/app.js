// Frontend JavaScript for RSS Generator

const API_BASE = '/api';

// Utility functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => alertDiv.remove(), 5000);
}

function showLoading(element) {
    element.innerHTML = '<div class="loading"><div class="spinner"></div><p>Loading...</p></div>';
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showAlert('Copied to clipboard!', 'success');
    }).catch(err => {
        showAlert('Failed to copy to clipboard', 'error');
    });
}

// Feed management functions
async function loadFeeds() {
    const feedList = document.getElementById('feedList');
    if (!feedList) return;
    
    showLoading(feedList);
    
    try {
        const response = await fetch(`${API_BASE}/feeds`);
        const data = await response.json();
        
        if (data.feeds.length === 0) {
            feedList.innerHTML = '<p>No feeds created yet. <a href="/create">Create your first feed</a>.</p>';
            return;
        }
        
        feedList.innerHTML = data.feeds.map(feed => `
            <div class="feed-item">
                <div class="feed-info">
                    <h3>${escapeHtml(feed.name)}</h3>
                    <p>${escapeHtml(feed.source_url)}</p>
                    <p class="meta">
                        <span>Created: ${new Date(feed.created_at).toLocaleDateString()}</span>
                        ${feed.last_fetched ? `<span>Last fetched: ${new Date(feed.last_fetched).toLocaleDateString()}</span>` : ''}
                        <span>Status: ${feed.is_active ? '✓ Active' : '✗ Inactive'}</span>
                    </p>
                </div>
                <div class="feed-actions">
                    <button class="btn btn-sm btn-primary" onclick="viewFeed('${feed.id}')">View RSS</button>
                    <button class="btn btn-sm btn-secondary" onclick="copyFeedUrl('${feed.id}')">Copy URL</button>
                    <button class="btn btn-sm btn-secondary" onclick="editFeed('${feed.id}')">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteFeed('${feed.id}')">Delete</button>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        feedList.innerHTML = '<p class="alert alert-error">Error loading feeds</p>';
        console.error('Error loading feeds:', error);
    }
}

function viewFeed(feedId) {
    window.open(`/rss/${feedId}`, '_blank');
}

function copyFeedUrl(feedId) {
    const url = `${window.location.origin}/rss/${feedId}`;
    copyToClipboard(url);
}

function editFeed(feedId) {
    window.location.href = `/configure/${feedId}`;
}

async function deleteFeed(feedId) {
    if (!confirm('Are you sure you want to delete this feed?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/feeds/${feedId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showAlert('Feed deleted successfully', 'success');
            loadFeeds();
        } else {
            showAlert('Error deleting feed', 'error');
        }
    } catch (error) {
        showAlert('Error deleting feed', 'error');
        console.error('Error deleting feed:', error);
    }
}

// Create feed form
async function handleCreateFeed(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const feedData = {
        name: formData.get('name'),
        source_url: formData.get('source_url'),
        feed_config: {
            title: formData.get('feed_title'),
            description: formData.get('feed_description'),
            link: formData.get('source_url')
        },
        item_selectors: {
            items: formData.get('items_xpath'),
            title: formData.get('title_xpath') || null,
            link: formData.get('link_xpath') || null,
            description: formData.get('description_xpath') || null,
            pubDate: formData.get('pubdate_xpath') || null,
            author: formData.get('author_xpath') || null,
            category: formData.get('category_xpath') || null,
            image: formData.get('image_xpath') || null
        },
        detail_extraction: {
            enabled: formData.get('enable_detail_extraction') === 'on',
            content: formData.get('content_xpath') || null,
            image: formData.get('detail_image_xpath') || null
        },
        options: {
            cache_ttl: parseInt(formData.get('cache_ttl')) || 3600,
            max_items: parseInt(formData.get('max_items')) || 50,
            enable_pagination: formData.get('enable_pagination') === 'on',
            respect_robots_txt: formData.get('respect_robots_txt') === 'on',
            request_delay: parseFloat(formData.get('request_delay')) || 1.0
        }
    };
    
    try {
        const response = await fetch(`${API_BASE}/feeds`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(feedData)
        });
        
        if (response.ok) {
            const result = await response.json();
            showAlert('Feed created successfully!', 'success');
            setTimeout(() => {
                window.location.href = '/manage';
            }, 1500);
        } else {
            const error = await response.json();
            showAlert(`Error: ${error.detail}`, 'error');
        }
    } catch (error) {
        showAlert('Error creating feed', 'error');
        console.error('Error creating feed:', error);
    }
}

// Test XPath
async function testXPath() {
    const url = document.getElementById('source_url').value;
    const xpath = document.getElementById('test_xpath').value;
    const resultsDiv = document.getElementById('xpath_results');
    
    if (!url || !xpath) {
        showAlert('Please enter both URL and XPath', 'error');
        return;
    }
    
    showLoading(resultsDiv);
    
    try {
        const response = await fetch(`${API_BASE}/feeds/test-xpath`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url, xpath })
        });
        
        const result = await response.json();
        
        if (result.success) {
            resultsDiv.innerHTML = `
                <h4>Results (${result.results.length}):</h4>
                <ul>
                    ${result.results.map(r => `<li>${escapeHtml(r)}</li>`).join('')}
                </ul>
            `;
        } else {
            resultsDiv.innerHTML = `<p class="alert alert-error">${escapeHtml(result.error)}</p>`;
        }
    } catch (error) {
        resultsDiv.innerHTML = '<p class="alert alert-error">Error testing XPath</p>';
        console.error('Error testing XPath:', error);
    }
}

// Preview feed
async function previewFeed() {
    const feedId = document.getElementById('feed_id')?.value;
    const previewDiv = document.getElementById('preview_results');
    
    if (!feedId || !previewDiv) return;
    
    showLoading(previewDiv);
    
    try {
        const response = await fetch(`${API_BASE}/feeds/${feedId}/preview`);
        const result = await response.json();
        
        if (result.success && result.items.length > 0) {
            previewDiv.innerHTML = result.items.map(item => `
                <div class="preview-item">
                    <h4>${escapeHtml(item.title || 'No title')}</h4>
                    <p>${escapeHtml(item.description || 'No description')}</p>
                    ${item.link ? `<p><a href="${escapeHtml(item.link)}" target="_blank">View link</a></p>` : ''}
                    <div class="meta">
                        ${item.author ? `<span>Author: ${escapeHtml(item.author)}</span>` : ''}
                        ${item.pubDate ? `<span>Date: ${new Date(item.pubDate).toLocaleDateString()}</span>` : ''}
                        ${item.category ? `<span>Categories: ${item.category.join(', ')}</span>` : ''}
                    </div>
                </div>
            `).join('');
        } else {
            previewDiv.innerHTML = `<p class="alert alert-error">${escapeHtml(result.error || 'No items found')}</p>`;
        }
    } catch (error) {
        previewDiv.innerHTML = '<p class="alert alert-error">Error previewing feed</p>';
        console.error('Error previewing feed:', error);
    }
}

// Helper function to escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Load feeds on manage page
    if (document.getElementById('feedList')) {
        loadFeeds();
    }
    
    // Setup create feed form
    const createForm = document.getElementById('createFeedForm');
    if (createForm) {
        createForm.addEventListener('submit', handleCreateFeed);
    }
});
