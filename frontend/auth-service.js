/**
 * AuthService
 * Coordinates authentication logic, login/registration, and automatic page lock control.
 */
const AuthService = {
    /**
     * Authenticates with credentials and establishes a secure session.
     */
    async login(username, password) {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        const response = await window.api.post('/login', formData);
        if (!response.ok) {
            const errData = await response.json();
            throw errData;
        }

        const data = await response.json();
        
        // Store the raw master password transiently in sessionStorage.
        // The backend's crypto.py performs its own PBKDF2 key derivation
        // with per-record random salts, so it requires the original password.
        window.SessionManager.saveSession(data.access_token, username, password);
        return data;
    },

    /**
     * Creates a new user profile on the backend.
     */
    async register(username, email, password) {
        const response = await window.api.post('/register', { username, email, password });
        if (!response.ok) {
            const errData = await response.json();
            throw errData;
        }
        return response.json();
    },

    /**
     * Terminate active session and redirect.
     */
    logout() {
        window.SessionManager.clearSession();
        window.location.href = "index.html";
    },

    /**
     * Handles auth enforcement rules and redirects.
     */
    checkAuth() {
        const isIndex = window.location.pathname.endsWith("index.html") || 
                        window.location.pathname.endsWith("/") ||
                        window.location.pathname === "";
        const session = window.SessionManager.getSession();
        
        if (!session) {
            if (!isIndex) {
                console.warn("[AuthService] No active session. Access denied.");
                window.location.href = "index.html";
            }
        } else {
            if (isIndex) {
                window.location.href = "dashboard.html";
            }
        }
    }
};

window.AuthService = AuthService;

// Execute authentication guard immediately on DOM Ready
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => window.AuthService.checkAuth());
} else {
    window.AuthService.checkAuth();
}
