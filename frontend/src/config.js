// src/config.js

// Sistemin lokalde mi yoksa gerçek sunucuda mı çalıştığını otomatik anlar
const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

export const API_BASE = isLocal 
    ? 'http://127.0.0.1:8000/api'  // Kendi bilgisayarında test ederken burası çalışır
    : 'https://api.seninsiten.com/api'; // Gerçek sunucuya yüklediğinde burası çalışır