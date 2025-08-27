export const metadata = {
  title: "Global Brain",
  description: "Your AI study partner",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header style={{ padding: 12, borderBottom: "1px solid #eee", display: "flex", gap: 12 }}>
          <a href="/">Home</a>
          <a href="/docs">Documents</a>
          <a href="/tutor">Tutor</a>
          <a href="/dashboard">Dashboard</a>
        </header>
        <div>
          {children}
        </div>
      </body>
    </html>
  );
}
