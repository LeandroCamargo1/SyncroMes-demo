// ══════════════════════════════════════════════════════════════
// Firebase — Inicialização centralizada (projeto syncro-mes)
// ══════════════════════════════════════════════════════════════
import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: "AIzaSyA58aAskep_4rxq5aZxZ6AzRECMM9Iqic8",
  authDomain: "syncro-mes.firebaseapp.com",
  projectId: "syncro-mes",
  storageBucket: "syncro-mes.firebasestorage.app",
  messagingSenderId: "769561755524",
  appId: "1:769561755524:web:e2d75bb472865d9a8be7d1",
};

const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);
export const auth = getAuth(app);
export default app;
