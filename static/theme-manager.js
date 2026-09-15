/**
 * Theme Manager
 * Handles dark/light mode toggle with persistent storage
 */

class ThemeManager {
    constructor() {
        this.STORAGE_KEY = 'nexus-theme';
        this.DARK_MODE = 'dark';
        this.LIGHT_MODE = 'light';
        this.AUTO_MODE = 'auto';

        // Initialize theme on page load
        this.initializeTheme();

        // Listen for system theme changes
        this.watchSystemTheme();
    }

    /**
     * Initialize theme from storage or system preference
     */
    initializeTheme() {
        const savedTheme = this.getStoredTheme();

        if (savedTheme) {
            this.setTheme(savedTheme);
        } else {
            // Use system preference
            if (this.prefersDarkMode()) {
                this.setTheme(this.DARK_MODE);
            } else {
                this.setTheme(this.LIGHT_MODE);
            }
        }

        this.updateToggleButton();
    }

    /**
     * Get stored theme preference
     */
    getStoredTheme() {
        try {
            return localStorage.getItem(this.STORAGE_KEY);
        } catch (e) {
            return null;
        }
    }

    /**
     * Save theme preference to storage
     */
    saveTheme(theme) {
        try {
            localStorage.setItem(this.STORAGE_KEY, theme);
        } catch (e) {
            console.warn('Could not save theme preference:', e);
        }
    }

    /**
     * Check if system prefers dark mode
     */
    prefersDarkMode() {
        return window.matchMedia &&
               window.matchMedia('(prefers-color-scheme: dark)').matches;
    }

    /**
     * Watch for system theme changes
     */
    watchSystemTheme() {
        if (!window.matchMedia) return;

        const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');

        // Modern browsers
        if (darkModeQuery.addEventListener) {
            darkModeQuery.addEventListener('change', (e) => {
                const storedTheme = this.getStoredTheme();
                // Only auto-switch if no explicit preference is stored
                if (!storedTheme) {
                    this.setTheme(e.matches ? this.DARK_MODE : this.LIGHT_MODE);
                    this.updateToggleButton();
                }
            });
        } else if (darkModeQuery.addListener) {
            // Legacy support
            darkModeQuery.addListener((e) => {
                const storedTheme = this.getStoredTheme();
                if (!storedTheme) {
                    this.setTheme(e.matches ? this.DARK_MODE : this.LIGHT_MODE);
                    this.updateToggleButton();
                }
            });
        }
    }

    /**
     * Set theme (dark or light)
     */
    setTheme(theme) {
        const html = document.documentElement;

        if (theme === this.DARK_MODE) {
            html.setAttribute('data-theme', 'dark');
            document.body.classList.add('dark-mode');
            document.body.classList.remove('light-mode');
        } else {
            html.setAttribute('data-theme', 'light');
            document.body.classList.add('light-mode');
            document.body.classList.remove('dark-mode');
        }

        // Dispatch custom event for other components
        window.dispatchEvent(new CustomEvent('theme-changed', {
            detail: { theme: theme }
        }));
    }

    /**
     * Toggle between dark and light modes
     */
    toggleTheme() {
        const current = this.getCurrentTheme();
        const newTheme = current === this.DARK_MODE ? this.LIGHT_MODE : this.DARK_MODE;

        this.setTheme(newTheme);
        this.saveTheme(newTheme);
        this.updateToggleButton();

        return newTheme;
    }

    /**
     * Get current theme
     */
    getCurrentTheme() {
        return document.documentElement.getAttribute('data-theme') || this.LIGHT_MODE;
    }

    /**
     * Update toggle button appearance
     */
    updateToggleButton() {
        const btn = document.getElementById('themeToggleBtn');
        if (!btn) return;

        const current = this.getCurrentTheme();

        if (current === this.DARK_MODE) {
            btn.innerHTML = '☀️'; // Sun icon for light mode
            btn.title = 'Switch to Light Mode';
            btn.setAttribute('aria-label', 'Switch to Light Mode');
        } else {
            btn.innerHTML = '🌙'; // Moon icon for dark mode
            btn.title = 'Switch to Dark Mode';
            btn.setAttribute('aria-label', 'Switch to Dark Mode');
        }
    }

    /**
     * Get theme statistics for analytics
     */
    getThemeStats() {
        return {
            current: this.getCurrentTheme(),
            stored: this.getStoredTheme(),
            systemPreference: this.prefersDarkMode() ? 'dark' : 'light'
        };
    }
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.themeManager = new ThemeManager();
    });
} else {
    window.themeManager = new ThemeManager();
}

/**
 * Public API function to toggle theme
 */
function toggleTheme() {
    if (window.themeManager) {
        return window.themeManager.toggleTheme();
    }
}

/**
 * Get current theme
 */
function getCurrentTheme() {
    if (window.themeManager) {
        return window.themeManager.getCurrentTheme();
    }
    return 'light';
}
