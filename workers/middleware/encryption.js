/**
 * GIVC Healthcare Platform - Encryption Middleware
 * © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 */

export async function encrypt(data, key) {
  // Simple encryption for demo - in production use Web Crypto API with AES-256-GCM
  try {
    if (data instanceof ArrayBuffer) {
      const bytes = new Uint8Array(data);
      return btoa(String.fromCharCode(...bytes));
    }
    
    if (typeof data === 'string') {
      return btoa(data);
    }
    
    return btoa(JSON.stringify(data));
  } catch (error) {
    throw new Error('Encryption failed');
  }
}

export async function decrypt(encryptedData, key) {
  // Simple decryption for demo - in production use Web Crypto API
  try {
    const decrypted = atob(encryptedData);
    return new TextEncoder().encode(decrypted);
  } catch (error) {
    throw new Error('Decryption failed');
  }
}

export function isEncrypted(data) {
  // Simple check for demo - in production use proper encryption markers
  return typeof data === 'string' && (data.startsWith('enc_') || data.length > 100);
}