import Head from 'next/head';

export default function Home() {
  return (
    <>
      <Head>
        <title>Global Brain</title>
      </Head>
      <main className="flex flex-col items-center justify-center h-screen bg-gray-50">
        <h1 className="text-4xl font-bold mb-4">Global Brain — Student Edition</h1>
        <p className="text-lg mb-8 max-w-xl text-center">
          Your AI study partner that organizes notes, tutors you at your level, and tracks progress.
        </p>
        <a
          href="/tutor"
          className="rounded bg-blue-600 px-6 py-3 text-white hover:bg-blue-700 transition"
        >
          Start Brain Boost
        </a>
      </main>
    </>
  );
}