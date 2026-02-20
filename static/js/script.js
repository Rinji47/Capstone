/* ============================================
   DJANGO BLOG - VANILLA JAVASCRIPT
   ============================================ */

// ============================================
// 1. DARK MODE TOGGLE
// ============================================

const themeToggle = document.getElementById('themeToggle');
const htmlElement = document.documentElement;
const body = document.body;

// Check for saved theme preference or default to light mode
function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = savedTheme || (prefersDark ? 'dark' : 'light');

    setTheme(theme);
}

function setTheme(theme) {
    if (theme === 'dark') {
        body.classList.add('dark-mode');
        localStorage.setItem('theme', 'dark');
        updateThemeIcon('light');
    } else {
        body.classList.remove('dark-mode');
        localStorage.setItem('theme', 'light');
        updateThemeIcon('dark');
    }
}

function updateThemeIcon(nextTheme) {
    if (themeToggle) {
        const icon = themeToggle.querySelector('i');
        if (nextTheme === 'light') {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
        } else {
            icon.classList.remove('fa-sun');
            icon.classList.add('fa-moon');
        }
    }
}

function toggleTheme() {
    const currentTheme = body.classList.contains('dark-mode') ? 'dark' : 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
}

// Event listeners
if (themeToggle) {
    themeToggle.addEventListener('click', toggleTheme);
}

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', initTheme);

// ============================================
// 2. FORM VALIDATION
// ============================================

function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function validatePassword(password) {
    return password.length >= 6;
}

function validateUsername(username) {
    return username.length >= 3 && username.length <= 30;
}

// Add event listeners to form fields for real-time validation
function initFormValidation() {
    const forms = document.querySelectorAll('.auth-form');

    forms.forEach(form => {
        const inputs = form.querySelectorAll('input');

        inputs.forEach(input => {
            input.addEventListener('blur', function () {
                validateField(this);
            });
        });
    });
}

function validateField(field) {
    const fieldName = field.name;
    let isValid = true;
    let errorMessage = '';

    switch (fieldName) {
        case 'email':
            isValid = validateEmail(field.value);
            errorMessage = 'Please enter a valid email address';
            break;
        case 'password1':
        case 'password':
            isValid = validatePassword(field.value);
            errorMessage = 'Password must be at least 6 characters';
            break;
        case 'username':
            isValid = validateUsername(field.value);
            errorMessage = 'Username must be between 3 and 30 characters';
            break;
    }

    if (!isValid && field.value) {
        field.classList.add('invalid');
        showFieldError(field, errorMessage);
    } else {
        field.classList.remove('invalid');
        clearFieldError(field);
    }
}

function showFieldError(field, message) {
    clearFieldError(field);
    const errorEl = document.createElement('span');
    errorEl.className = 'field-error';
    errorEl.textContent = message;
    field.parentElement.appendChild(errorEl);
}

function clearFieldError(field) {
    const existingError = field.parentElement.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}

// ============================================
// 3. POST FILTERING
// ============================================

function initPostFiltering() {
    const categoryFilter = document.getElementById('categoryFilter');
    const searchInput = document.getElementById('searchInput');
    const postsGrid = document.getElementById('postsGrid');

    if (!postsGrid) return;

    const postCards = document.querySelectorAll('.post-card');

    function filterPosts() {
        const selectedCategory = categoryFilter?.value.toLowerCase() || '';
        const searchTerm = searchInput?.value.toLowerCase() || '';

        let visibleCount = 0;

        postCards.forEach(card => {
            const category = card.dataset.category?.toLowerCase() || '';
            const title = card.dataset.title?.toLowerCase() || '';

            const categoryMatch = !selectedCategory || category === selectedCategory;
            const searchMatch = !searchTerm || title.includes(searchTerm);

            if (categoryMatch && searchMatch) {
                card.style.display = '';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });

        // Show/hide no results message
        showNoResultsMessage(visibleCount === 0);
    }

    function showNoResultsMessage(show) {
        let noResultsEl = postsGrid.querySelector('.no-posts');

        if (show && !noResultsEl) {
            noResultsEl = document.createElement('div');
            noResultsEl.className = 'no-posts';
            noResultsEl.innerHTML = `
                <i class="fas fa-search"></i>
                <p>No posts found. Try adjusting your filters.</p>
            `;
            postsGrid.appendChild(noResultsEl);
        } else if (!show && noResultsEl) {
            noResultsEl.remove();
        }
    }

    if (categoryFilter) {
        categoryFilter.addEventListener('change', filterPosts);
    }

    if (searchInput) {
        searchInput.addEventListener('input', filterPosts);
    }
}

// ============================================
// 4. LIKE FUNCTIONALITY
// ============================================

function initLikeButtons() {
    // Handle like buttons with AJAX — no page reload
    document.querySelectorAll('.like-button').forEach(function (btn) {
        const form = btn.closest('form');
        const isAnchor = btn.tagName === 'A' || btn.closest('a.stat, a.like-button');

        function doLike(e) {
            e.preventDefault();

            // Figure out the URL
            let url;
            if (form) {
                url = form.getAttribute('action');
            } else {
                url = btn.getAttribute('href') || btn.closest('a') && btn.closest('a').getAttribute('href');
            }
            if (!url) return;

            // Get CSRF from cookie
            const match = document.cookie.match(/csrftoken=([^;]+)/);
            const csrf = match ? match[1] : '';

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrf,
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'csrfmiddlewaretoken=' + csrf,
            })
                .then(function (res) {
                    if (res.status === 401) { window.location.href = '/login/'; return null; }
                    return res.json();
                })
                .then(function (data) {
                    if (!data) return;

                    // Toggle liked visual state on the button
                    if (data.liked) {
                        btn.classList.add('liked');
                    } else {
                        btn.classList.remove('liked');
                    }

                    // Update the count — try every known selector
                    var countEl = btn.querySelector('#likeCount')
                        || btn.querySelector('.like-count')
                        || btn.querySelector('span');
                    if (countEl) {
                        countEl.textContent = data.count;
                    }
                })
                .catch(function (err) { console.error('Like AJAX error:', err); });
        }

        if (form) {
            form.addEventListener('submit', doLike);
        } else {
            // anchor or bare button
            var clickTarget = btn.tagName === 'A' ? btn : (btn.closest('a') || btn);
            clickTarget.addEventListener('click', doLike);
        }
    });
}

// ============================================
// 5. COMMENT FORM
// ============================================

function initCommentForm() {
    const commentForm = document.querySelector('.comment-form');

    if (!commentForm) return;

    const textarea = commentForm.querySelector('.comment-textarea');
    const submitButton = commentForm.querySelector('.comment-button');

    if (textarea) {
        textarea.addEventListener('input', function () {
            submitButton.disabled = !this.value.trim();
        });
    }
}

// ============================================
// 6. PROFILE TABS
// ============================================

function initProfileTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    if (tabButtons.length === 0) return;

    tabButtons.forEach(button => {
        button.addEventListener('click', function () {
            const tabName = this.dataset.tab;

            // Remove active from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active to clicked button and corresponding content
            this.classList.add('active');
            const tabContent = document.getElementById(tabName + '-tab');
            if (tabContent) {
                tabContent.classList.add('active');
            }
        });
    });
}

// ============================================
// 7. SHARE BUTTON
// ============================================

function initShareButton() {
    const shareButton = document.querySelector('.share-button');

    if (!shareButton) return;

    shareButton.addEventListener('click', function () {
        const title = document.querySelector('.post-detail-title')?.textContent || 'Check this out';
        const url = window.location.href;

        if (navigator.share) {
            navigator.share({
                title: title,
                url: url
            }).catch(err => console.log('Error sharing:', err));
        } else {
            // Fallback: copy to clipboard
            copyToClipboard(url);
        }
    });
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Show feedback
        const button = document.querySelector('.share-button');
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check"></i> Copied!';

        setTimeout(() => {
            button.innerHTML = originalText;
        }, 2000);
    });
}

// ============================================
// 8. SMOOTH SCROLL
// ============================================

function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));

            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// ============================================
// 9. MOBILE MENU TOGGLE
// ============================================

function initMobileMenu() {
    const hamburger = document.querySelector('.mobile-menu-toggle');
    const menu = document.querySelector('.navbar-menu');

    if (!hamburger || !menu) return;

    hamburger.addEventListener('click', function () {
        menu.classList.toggle('active');
        this.classList.toggle('active');
    });
}

// ============================================
// 10. ALERT AUTO-DISMISS
// ============================================

function initAlertAutoDismiss() {
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.3s ease-out';
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });
}

// ============================================
// 11. FORM SUBMISSION VALIDATION
// ============================================

function initFormSubmission() {
    const forms = document.querySelectorAll('.auth-form');

    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            const inputs = this.querySelectorAll('input[required], textarea[required]');
            let isValid = true;

            inputs.forEach(input => {
                // Skip file inputs - they are optional
                if (input.type === 'file') return;
                if (!input.value.trim()) {
                    isValid = false;
                    input.style.borderColor = '#ef4444';
                } else {
                    input.style.borderColor = '';
                }
            });

            if (!isValid) {
                e.preventDefault();
            }
        });
    });
}

// ============================================
// 12. KEYBOARD NAVIGATION
// ============================================

function initKeyboardNavigation() {
    document.addEventListener('keydown', function (e) {
        // Close dropdowns on Escape
        if (e.key === 'Escape') {
            const dropdowns = document.querySelectorAll('.dropdown');
            dropdowns.forEach(dropdown => {
                dropdown.style.opacity = '0';
                dropdown.style.visibility = 'hidden';
            });
        }

        // Search on Ctrl+K or Cmd+K
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.focus();
            }
        }
    });
}

// ============================================
// 13. LAZY LOADING IMAGES
// ============================================

function initLazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');

    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    }
}

// ============================================
// 14. CSRF TOKEN HELPER
// ============================================

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ============================================
// 15. MAIN INITIALIZATION
// ============================================

function initializeApp() {
    // Run all initialization functions
    initTheme();
    initFormValidation();
    initPostFiltering();
    initLikeButtons();
    initCommentForm();
    initProfileTabs();
    initShareButton();
    initSmoothScroll();
    initMobileMenu();
    initAlertAutoDismiss();
    initFormSubmission();
    initKeyboardNavigation();
    initLazyLoadImages();
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

// ============================================
// 16. UTILITY FUNCTIONS
// ============================================

// Format date in user-friendly way
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', options);
}

// Truncate text with ellipsis
function truncateText(text, maxLength) {
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}

// Check if user prefers reduced motion
function prefersReducedMotion() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

// Debounce function for search
function debounce(func, delay) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

// Apply debouncing to search input
document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        const debouncedFilter = debounce(function () {
            document.getElementById('categoryFilter')?.dispatchEvent(new Event('change'));
        }, 300);

        searchInput.addEventListener('input', debouncedFilter);
    }
});

// Export for use in other scripts if needed
window.BlogApp = {
    formatDate,
    truncateText,
    prefersReducedMotion,
    debounce,
    getCookie,
    toggleTheme,
    validateEmail,
    validatePassword,
    validateUsername
};
