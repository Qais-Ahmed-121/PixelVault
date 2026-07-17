/**
 * API Client
 * Centralized fetch wrapper that automatically appends Authorization headers
 * and handles unauthorized (401) responses uniformly.
 */
const API_URL = "http://127.0.0.1:8000";

const api = {
    async request(endpoint, options = {}) {
        const url = endpoint.startsWith("http") ? endpoint : `${API_URL}${endpoint}`;
        
        options.headers = options.headers || {};
        
        // Automatically inject Bearer token if active session exists
        const session = window.SessionManager.getSession();
        if (session && session.token) {
            options.headers['Authorization'] = `Bearer ${session.token}`;
        }
        
        // Default content type to JSON unless it's FormData
        if (options.body && !(options.body instanceof FormData) && !options.headers['Content-Type']) {
            options.headers['Content-Type'] = 'application/json';
        }

        try {
            const response = await fetch(url, options);
            
            // Globally handle 401 Unauthorized errors
            if (response.status === 401) {
                console.warn("[API] Session unauthorized or expired. Redirecting to login.");
                window.SessionManager.clearSession();
                
                // Avoid infinite redirect loop if already on login page
                if (!window.location.pathname.endsWith("index.html") && window.location.pathname !== "") {
                    window.location.href = "index.html";
                }
            }
            
            return response;
        } catch (error) {
            console.error("[API Net Error]", error);
            throw error;
        }
    },

    async get(endpoint, headers = {}) {
        return this.request(endpoint, { method: 'GET', headers });
    },

    async post(endpoint, body, headers = {}) {
        const isForm = body instanceof FormData;
        return this.request(endpoint, {
            method: 'POST',
            headers,
            body: isForm ? body : JSON.stringify(body)
        });
    },

    async delete(endpoint, headers = {}) {
        return this.request(endpoint, { method: 'DELETE', headers });
    }
};

window.api = api;
