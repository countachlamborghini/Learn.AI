import { Inter } from 'next/font/google';
import '../styles/globals.css';
import { Providers } from './providers';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'Global Brain - AI Study Companion',
  description: 'Your AI study partner that organizes notes, tutors you at your level, and tracks progress',
  keywords: 'AI tutor, study companion, flashcards, learning, education',
  authors: [{ name: 'Global Brain Team' }],
  viewport: 'width=device-width, initial-scale=1',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} h-full bg-gray-50`}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}