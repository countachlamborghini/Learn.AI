'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { authService, User } from '@/lib/auth';
import { progressAPI } from '@/lib/api';
import { 
  Brain, 
  Upload, 
  MessageSquare, 
  Zap, 
  TrendingUp, 
  BookOpen,
  LogOut,
  User as UserIcon,
  Settings,
  FileText,
  Target,
  Clock
} from 'lucide-react';

interface ProgressOverview {
  total_mastery_score: number;
  weak_topics: Array<{
    topic: string;
    score: number;
  }>;
  current_streak: number;
  time_saved_this_week: number;
  total_practice_time: number;
  documents_processed: number;
  flashcards_created: number;
}

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [progress, setProgress] = useState<ProgressOverview | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const currentUser = await authService.getCurrentUser();
        if (!currentUser) {
          window.location.href = '/login';
          return;
        }
        setUser(currentUser);

        // Load progress data
        const progressData = await progressAPI.getOverview();
        setProgress(progressData.data);
      } catch (error) {
        console.error('Failed to load dashboard:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadDashboard();
  }, []);

  const handleLogout = () => {
    authService.logout();
    window.location.href = '/';
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <Brain className="h-8 w-8 text-blue-600" />
              <span className="text-xl font-bold text-gray-900">Global Brain</span>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <UserIcon className="h-5 w-5 text-gray-400" />
                <span className="text-sm text-gray-700">
                  {user?.first_name || user?.email}
                </span>
              </div>
              <Button variant="ghost" size="sm" onClick={handleLogout}>
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.first_name || 'Student'}!
          </h1>
          <p className="text-gray-600">
            Ready to continue your learning journey?
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Link href="/dashboard/upload">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer">
              <div className="flex items-center space-x-3">
                <div className="bg-blue-100 rounded-full p-3">
                  <Upload className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Upload Documents</h3>
                  <p className="text-sm text-gray-600">Add new study materials</p>
                </div>
              </div>
            </div>
          </Link>

          <Link href="/dashboard/tutor">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer">
              <div className="flex items-center space-x-3">
                <div className="bg-green-100 rounded-full p-3">
                  <MessageSquare className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Chat with Tutor</h3>
                  <p className="text-sm text-gray-600">Ask questions, get help</p>
                </div>
              </div>
            </div>
          </Link>

          <Link href="/dashboard/brain-boost">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer">
              <div className="flex items-center space-x-3">
                <div className="bg-purple-100 rounded-full p-3">
                  <Zap className="h-6 w-6 text-purple-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Brain Boost</h3>
                  <p className="text-sm text-gray-600">10-minute review session</p>
                </div>
              </div>
            </div>
          </Link>

          <Link href="/dashboard/progress">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer">
              <div className="flex items-center space-x-3">
                <div className="bg-orange-100 rounded-full p-3">
                  <TrendingUp className="h-6 w-6 text-orange-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">View Progress</h3>
                  <p className="text-sm text-gray-600">Track your learning</p>
                </div>
              </div>
            </div>
          </Link>
        </div>

        {/* Progress Overview */}
        {progress && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            {/* Mastery Score */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Mastery Score</h3>
                <Target className="h-5 w-5 text-blue-600" />
              </div>
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {Math.round(progress.total_mastery_score * 100)}%
              </div>
              <p className="text-sm text-gray-600">Overall learning progress</p>
            </div>

            {/* Current Streak */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Study Streak</h3>
                <Zap className="h-5 w-5 text-yellow-600" />
              </div>
              <div className="text-3xl font-bold text-yellow-600 mb-2">
                {progress.current_streak} days
              </div>
              <p className="text-sm text-gray-600">Keep it going!</p>
            </div>

            {/* Time Saved */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Time Saved</h3>
                <Clock className="h-5 w-5 text-green-600" />
              </div>
              <div className="text-3xl font-bold text-green-600 mb-2">
                {progress.time_saved_this_week} min
              </div>
              <p className="text-sm text-gray-600">This week with AI help</p>
            </div>
          </div>
        )}

        {/* Recent Activity & Weak Areas */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Documents */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Recent Documents</h3>
              <Link href="/dashboard/documents">
                <Button variant="ghost" size="sm">
                  View all
                </Button>
              </Link>
            </div>
            <div className="space-y-3">
              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <FileText className="h-5 w-5 text-gray-400" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">No documents yet</p>
                  <p className="text-xs text-gray-500">Upload your first document to get started</p>
                </div>
              </div>
            </div>
          </div>

          {/* Weak Areas */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Focus Areas</h3>
              <Link href="/dashboard/progress">
                <Button variant="ghost" size="sm">
                  View details
                </Button>
              </Link>
            </div>
            <div className="space-y-3">
              {progress?.weak_topics && progress.weak_topics.length > 0 ? (
                progress.weak_topics.slice(0, 3).map((topic, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{topic.topic}</p>
                      <p className="text-xs text-gray-500">Mastery: {Math.round(topic.score * 100)}%</p>
                    </div>
                    <Button size="sm" variant="outline">
                      Practice
                    </Button>
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <BookOpen className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-sm text-gray-500">No weak areas identified yet</p>
                  <p className="text-xs text-gray-400">Complete some Brain Boosts to see your focus areas</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}