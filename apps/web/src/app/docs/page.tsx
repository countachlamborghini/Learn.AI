"use client";

import { useState } from "react";

export default function DocsPage() {
  const [file, setFile] = useState<File | null>(null);
  const [docId, setDocId] = useState<string | null>(null);
  const [cards, setCards] = useState<any[] | null>(null);
  const [loading, setLoading] = useState(false);
  const api = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  async function onUpload() {
    if (!file) return;
    setLoading(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const resp = await fetch(`${api}/v1/docs/upload`, { method: "POST", body: fd });
      const data = await resp.json();
      setDocId(data.document_id);
      const fc = await fetch(`${api}/v1/docs/${data.document_id}/flashcards`).then((r) => r.json());
      setCards(fc);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ padding: 24, maxWidth: 800, margin: "0 auto" }}>
      <h2>Documents</h2>
      <p>Upload a file and we will generate flashcards.</p>
      <input type="file" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
      <button onClick={onUpload} disabled={!file || loading} style={{ marginLeft: 12 }}>
        {loading ? "Uploading…" : "Upload"}
      </button>
      {docId && (
        <div style={{ marginTop: 16 }}>
          <div>Document ID: {docId}</div>
          <h3>Flashcards</h3>
          <ul>
            {(cards || []).map((c, idx) => (
              <li key={idx}>
                <strong>{c.front}</strong>
                <div>{c.back}</div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </main>
  );
}

