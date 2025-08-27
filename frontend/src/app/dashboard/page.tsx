'use client';

import { useQuery } from 'react-query';
import { 
  Zap, 
  Clock, 
  BookOpen, 
  TrendingUp, 
  FileText, 
  MessageCircle,
  Target,
  Calendar,
  Award,
  ChevronRight
} from 'lucide-react';
import Link from 'next/link';
import DashboardLayout from '../../components/layout/DashboardLayout';
import { progressApi } from '../../utils/api';
import { formatDuration, formatStreak, getScoreColor } from '../../utils/helpers';
import { ProgressOverview, WeakArea } from '../../types';

function DashboardContent() {
  // Fetch progress overview
  const { data: overview, isLoading: overviewLoading } = useQuery<ProgressOverview>(
    'progressOverview',
    progressApi.getOverview
  );

  // Fetch weak areas
  const { data: weakAreas, isLoading: weakAreasLoading } = useQuery<WeakArea[]>(
    'weakAreas',
    progressApi.getWeakAreas
  );

  if (overviewLoading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">Welcome back! 👋</h1>
        <p className="text-primary-100">
          Ready for today's learning session? You're on a {formatStreak(overview?.current_streak || 0)} streak!
        </p>
        <div className="mt-4">
          <Link
            href="/brain-boost"
            className="inline-flex items-center bg-white text-primary-600 font-semibold px-4 py-2 rounded-lg hover:bg-primary-50 transition-colors duration-200"
          >
            <Zap className="h-4 w-4 mr-2" />
            Start Brain Boost
          </Link>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="stat-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Study Streak</p>
              <p className="text-2xl font-bold text-gray-900">
                {overview?.current_streak || 0}
              </p>
              <p className="text-xs text-gray-500">days in a row 🔥</p>
            </div>
            <div className="p-3 bg-orange-100 rounded-full">
              <Calendar className="h-6 w-6 text-orange-600" />
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Study Time</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatDuration(overview?.this_week.study_time_minutes || 0)}
              </p>
              <p className="text-xs text-gray-500">this week</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <Clock className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Documents</p>
              <p className="text-2xl font-bold text-gray-900">
                {overview?.total_documents || 0}
              </p>
              <p className="text-xs text-gray-500">uploaded</p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <FileText className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Score</p>
              <p className={`text-2xl font-bold ${getScoreColor(overview?.brain_boost_average_score || 0)}`}>
                {Math.round(overview?.brain_boost_average_score || 0)}%
              </p>
              <p className="text-xs text-gray-500">Brain Boost</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <Award className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Start Brain Boost */}
        <Link href="/brain-boost" className="card card-hover group">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-primary-100 rounded-lg group-hover:bg-primary-200 transition-colors duration-200">
              <Zap className="h-6 w-6 text-primary-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900">Daily Brain Boost</h3>
              <p className="text-sm text-gray-600">10-minute focused review</p>
            </div>
            <ChevronRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600" />
          </div>
        </Link>

        {/* Chat with Tutor */}
        <Link href="/tutor" className="card card-hover group">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-blue-100 rounded-lg group-hover:bg-blue-200 transition-colors duration-200">
              <MessageCircle className="h-6 w-6 text-blue-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900">Ask Your Tutor</h3>
              <p className="text-sm text-gray-600">Get help with any topic</p>
            </div>
            <ChevronRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600" />
          </div>
        </Link>

        {/* Upload Documents */}
        <Link href="/upload" className="card card-hover group">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-green-100 rounded-lg group-hover:bg-green-200 transition-colors duration-200">
              <BookOpen className="h-6 w-6 text-green-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900">Upload Materials</h3>
              <p className="text-sm text-gray-600">Add PDFs, notes, slides</p>
            </div>
            <ChevronRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600" />
          </div>
        </Link>
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Weak Areas */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Areas to Focus On</h2>
            <Link
              href="/progress"
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              View all
            </Link>
          </div>
          
          {weakAreasLoading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="animate-pulse h-16 bg-gray-200 rounded-lg"></div>
              ))}
            </div>
          ) : weakAreas && weakAreas.length > 0 ? (
            <div className="space-y-3">
              {weakAreas.slice(0, 3).map((area, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{area.topic}</p>
                    <p className="text-sm text-gray-600">{area.recommended_action}</p>
                  </div>
                  <div className="text-right">
                    <span className={`text-sm font-medium ${getScoreColor(area.mastery_score)}`}>
                      {Math.round(area.mastery_score)}%
                    </span>
                    <div className={`text-xs px-2 py-1 rounded-full mt-1 ${
                      area.priority === 'high' ? 'bg-red-100 text-red-700' :
                      area.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-blue-100 text-blue-700'
                    }`}>
                      {area.priority} priority
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Target className="h-12 w-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600">Great job! No weak areas identified.</p>
              <p className="text-sm text-gray-500">Keep up the excellent work!</p>
            </div>
          )}
        </div>

        {/* Recent Activity */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
            <Link
              href="/progress"
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              View all
            </Link>
          </div>
          
          <div className="space-y-3">
            <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className="p-2 bg-primary-100 rounded-lg">
                <Zap className="h-4 w-4 text-primary-600" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">
                  Completed Brain Boost: Physics
                </p>
                <p className="text-xs text-gray-500">2 hours ago • Score: 85%</p>
              </div>
            </div>

            <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className="p-2 bg-green-100 rounded-lg">
                <BookOpen className="h-4 w-4 text-green-600" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">
                  Generated 15 flashcards from Chemistry notes
                </p>
                <p className="text-xs text-gray-500">Yesterday</p>
              </div>
            </div>

            <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className="p-2 bg-blue-100 rounded-lg">
                <MessageCircle className="h-4 w-4 text-blue-600" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">
                  Asked tutor about calculus derivatives
                </p>
                <p className="text-xs text-gray-500">2 days ago</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* This Week Summary */}
      <div className="card bg-gradient-to-r from-secondary-50 to-primary-50">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">This Week's Progress</h2>
        <div className="grid grid-cols-3 gap-6">
          <div className="text-center">
            <p className="text-2xl font-bold text-primary-600">
              {overview?.this_week.study_sessions || 0}
            </p>
            <p className="text-sm text-gray-600">Study Sessions</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-primary-600">
              {overview?.this_week.brain_boosts_completed || 0}
            </p>
            <p className="text-sm text-gray-600">Brain Boosts</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-primary-600">
              {overview?.total_flashcards || 0}
            </p>
            <p className="text-sm text-gray-600">Flashcards Created</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <DashboardLayout title="Dashboard" subtitle="Your learning overview">
      <DashboardContent />
    </DashboardLayout>
  );
}