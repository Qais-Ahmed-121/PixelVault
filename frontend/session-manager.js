/**
 * SessionManager
 * Manages the active user session securely inside sessionStorage.
 * Stores JWT token, username, and the derived encryption key.
 */
const SessionManager = {
    /**
     * Start a new secure session.
     * @param {string} token - JWT Access Token
     * @param {string} username 
     * @param {string} encryptionKey - Hex-derived PBKDF2 encryption key
     */
    saveSession(token, username, encryptionKey) {
        sessionStorage.setItem('token', token);
        sessionStorage.setItem('username', username);
        sessionStorage.setItem('encryptionKey', encryptionKey);
        
        // Expiry matches JWT timeout, set to 30 minutes.
        const expiry = Date.now() + 30 * 60 * 1000;
        sessionStorage.setItem('sessionExpiry', expiry.toString());
        
        // Remove legacy localStorage items to prevent state sync issues
        localStorage.removeItem('token');
        localStorage.removeItem('username');
    },

    /**
     * Retrieves active session details if valid.
     * @returns {object|null} session info or null if expired/invalid
     */
    getSession() {
        const token = sessionStorage.getItem('token');
        const username = sessionStorage.getItem('username');
        const encryptionKey = sessionStorage.getItem('encryptionKey');
        const expiryStr = sessionStorage.getItem('sessionExpiry');
        
        if (!token || !username || !encryptionKey || !expiryStr) {
            return null;
        }
        
        const expiry = parseInt(expiryStr, 10);
        if (Date.now() > expiry) {
            this.clearSession();
            return null;
        }
        
        // Refresh session expiry on user activity
        const newExpiry = Date.now() + 30 * 60 * 1000;
        sessionStorage.setItem('sessionExpiry', newExpiry.toString());
        
        return { token, username, encryptionKey };
    },

    clearSession() {
        sessionStorage.removeItem('token');
        sessionStorage.removeItem('username');
        sessionStorage.removeItem('encryptionKey');
        sessionStorage.removeItem('sessionExpiry');
        localStorage.removeItem('token');
        localStorage.removeItem('username');
    },

    isValid() {
        return this.getSession() !== null;
    }
};

window.SessionManager = SessionManager;
