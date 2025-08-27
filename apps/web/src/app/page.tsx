"use client";

import { useEffect, useState } from "react";

export default function HomePage() {
  const [apiStatus, setApiStatus] = useState<string>("checking…");
  useEffect(() => {
    const url = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    fetch(`${url}/health`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(() => setApiStatus("online"))
      .catch(() => setApiStatus("offline"));
  }, []);

  return (
    <main style={{ padding: 24, maxWidth: 960, margin: "0 auto" }}>
      <h1>Global Brain — Student Edition</h1>
      <p>Your AI study partner that organizes notes, tutors you, and tracks progress.</p>
      <div style={{ marginTop: 8, fontSize: 12, color: apiStatus === "online" ? "green" : "#a00" }}>
        API: {apiStatus}
      </div>
      <div style={{ display: "grid", gap: 16, gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", marginTop: 24 }}>
        <section style={{ border: "1px solid #eee", borderRadius: 8, padding: 16 }}>
          <h3>Today’s Brain Boost</h3>
          <p>10 minutes — personalized review</p>
          <button>Start</button>
        </section>
        <section style={{ border: "1px solid #eee", borderRadius: 8, padding: 16 }}>
          <h3>Weak Topics</h3>
          <p>Kinematics, Stoichiometry</p>
        </section>
        <section style={{ border: "1px solid #eee", borderRadius: 8, padding: 16 }}>
          <h3>Streak</h3>
          <p>3 days</p>
        </section>
      </div>
    </main>
  );
}
