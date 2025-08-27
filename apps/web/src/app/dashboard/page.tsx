"use client";

import { useEffect, useState } from "react";

export default function DashboardPage() {
  const [overview, setOverview] = useState<any | null>(null);
  const api = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    fetch(`${api}/v1/progress/overview`).then((r) => r.json()).then(setOverview).catch(() => setOverview(null));
  }, [api]);

  return (
    <main style={{ padding: 24, maxWidth: 800, margin: "0 auto" }}>
      <h2>Dashboard</h2>
      {overview ? (
        <div>
          <div>Streak: {overview.streak_days} days</div>
          <div>Time saved this week: {overview.time_saved_minutes_this_week} mins</div>
          <h3>Mastery</h3>
          <ul>
            {Object.entries(overview.mastery).map(([topic, score]) => (
              <li key={topic}>
                {topic}: {String(score)}%
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <div>Loading…</div>
      )}
    </main>
  );
}

