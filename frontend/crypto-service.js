/**
 * CryptoService
 * Handles cryptographic operations on the client-side.
 * Derives encryption key from the Master Password using PBKDF2.
 */
const CryptoService = {
    /**
     * Derives a 256-bit key from a password and username using PBKDF2.
     * @param {string} password - The master password
     * @param {string} username - The username (used as salt)
     * @returns {Promise<string>} Hex representation of the derived key.
     */
    async deriveKey(password, username) {
        if (!password || !username) {
            throw new Error("Password and username are required for key derivation.");
        }
        
        const encoder = new TextEncoder();
        const passwordBytes = encoder.encode(password);
        // Normalize username salt to lowercase to ensure consistency
        const saltBytes = encoder.encode(username.trim().toLowerCase());

        // Import the raw password as a PBKDF2 base key
        const baseKey = await window.crypto.subtle.importKey(
            "raw",
            passwordBytes,
            "PBKDF2",
            false,
            ["deriveBits", "deriveKey"]
        );

        // Derive 256 bits (32 bytes) of key material
        const derivedBits = await window.crypto.subtle.deriveBits(
            {
                name: "PBKDF2",
                salt: saltBytes,
                iterations: 100000,
                hash: "SHA-256"
            },
            baseKey,
            256
        );

        // Convert the derived bytes to a hex string
        const keyArray = new Uint8Array(derivedBits);
        return Array.from(keyArray)
            .map(b => b.toString(16).padStart(2, '0'))
            .join('');
    }
};

window.CryptoService = CryptoService;
