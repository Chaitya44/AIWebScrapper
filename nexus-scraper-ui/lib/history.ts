import {
    collection,
    addDoc,
    getDocs,
    deleteDoc,
    doc,
    query,
    orderBy,
    limit,
    serverTimestamp,
} from "firebase/firestore";
import { db } from "@/lib/firebase";

export interface HistoryEntry {
    id?: string;
    url: string;
    timestamp: string;
    data: Record<string, any[]>;
    schema: Record<string, any>;
    itemCount: number;
}

const COLLECTION_PATH = (uid: string) => `users/${uid}/history`;
const MAX_HISTORY = 5;

/**
 * Save a scrape result to Firestore. Enforces FIFO limit of 5.
 */
export async function saveHistory(uid: string, entry: Omit<HistoryEntry, "id">) {
    if (!db) return;
    const colRef = collection(db, COLLECTION_PATH(uid));

    // Add the new entry
    await addDoc(colRef, {
        ...entry,
        createdAt: serverTimestamp(),
    });

    // Enforce FIFO: if more than MAX_HISTORY, delete oldest
    const allQuery = query(colRef, orderBy("createdAt", "asc"));
    const snapshot = await getDocs(allQuery);
    if (snapshot.size > MAX_HISTORY) {
        const toDelete = snapshot.size - MAX_HISTORY;
        const docs = snapshot.docs.slice(0, toDelete);
        for (const d of docs) {
            await deleteDoc(doc(db, COLLECTION_PATH(uid), d.id));
        }
    }
}

/**
 * Load all history entries for a user, newest first.
 */
export async function loadHistory(uid: string): Promise<HistoryEntry[]> {
    if (!db) return [];
    const colRef = collection(db, COLLECTION_PATH(uid));
    const q = query(colRef, orderBy("createdAt", "desc"), limit(MAX_HISTORY));
    const snapshot = await getDocs(q);

    return snapshot.docs.map((d) => {
        const data = d.data();
        return {
            id: d.id,
            url: data.url,
            timestamp: data.timestamp,
            data: data.data,
            schema: data.schema,
            itemCount: data.itemCount,
        };
    });
}

/**
 * Delete a single history entry.
 */
export async function deleteHistoryEntry(uid: string, docId: string) {
    if (!db) return;
    await deleteDoc(doc(db, COLLECTION_PATH(uid), docId));
}

/**
 * Clear all history for a user.
 */
export async function clearHistory(uid: string) {
    if (!db) return;
    const colRef = collection(db, COLLECTION_PATH(uid));
    const snapshot = await getDocs(colRef);
    for (const d of snapshot.docs) {
        await deleteDoc(doc(db, COLLECTION_PATH(uid), d.id));
    }
}
