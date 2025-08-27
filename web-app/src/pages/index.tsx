import Head from 'next/head';

export default function Home() {
  return (
    <>
      <Head>
        <title>Global Brain</title>
      </Head>
      <main className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-b from-blue-50 to-white px-4">
        <h1 className="text-5xl font-extrabold text-gray-900 mb-6 text-center leading-tight">
          Study smarter with <span className="text-primary">Global Brain</span>
        </h1>
        <p className="text-lg text-gray-600 mb-10 max-w-2xl text-center">
          Organize your notes, chat with an adaptive AI tutor, and boost your mastery in minutes a day.
        </p>
        <div className="flex gap-4">
          <a
            href="/tutor"
            className="rounded-lg bg-primary px-8 py-3 text-white font-medium shadow hover:bg-primary-dark transition"
          >
            Start Brain Boost
          </a>
          <a
            href="/docs"
            className="rounded-lg bg-white border border-primary px-8 py-3 text-primary font-medium shadow hover:bg-blue-100 transition"
          >
            Upload Notes
          </a>
        </div>
      </main>
    </>
  );
}