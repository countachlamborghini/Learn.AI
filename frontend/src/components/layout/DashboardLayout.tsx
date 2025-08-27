'use client';

import { AuthProvider } from '../../hooks/useAuth';
import { useAuthGuard } from '../../hooks/useAuth';
import Sidebar from './Sidebar';
import Header from './Header';

interface DashboardLayoutProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
}

function DashboardContent({ children, title, subtitle }: DashboardLayoutProps) {
  const { isAuthenticated, isLoading } = useAuthGuard();

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Will redirect to login
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header title={title} subtitle={subtitle} />
        <main className="flex-1 overflow-auto">
          <div className="p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}

export default function DashboardLayout({ children, title, subtitle }: DashboardLayoutProps) {
  return (
    <AuthProvider>
      <DashboardContent title={title} subtitle={subtitle}>
        {children}
      </DashboardContent>
    </AuthProvider>
  );
}