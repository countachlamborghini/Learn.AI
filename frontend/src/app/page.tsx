'use client';

import Link from 'next/link';
import { Brain, BookOpen, MessageCircle, Zap, TrendingUp, Users } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50">
      {/* Navigation */}
      <nav className="relative px-6 py-4">
        <div className="mx-auto max-w-7xl flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-600">
              <Brain className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">Global Brain</span>
          </div>
          <div className="flex items-center space-x-4">
            <Link
              href="/login"
              className="text-gray-600 hover:text-gray-900 font-medium"
            >
              Log in
            </Link>
            <Link
              href="/signup"
              className="btn-primary"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative px-6 py-16">
        <div className="mx-auto max-w-4xl text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Your AI study partner that{' '}
            <span className="text-gradient">learns with you</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Upload your materials, get instant flashcards, chat with an adaptive tutor, 
            and track your progress with personalized Brain Boosts — all in minutes a day.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/signup"
              className="btn-primary text-lg px-8 py-3"
            >
              Start Learning Free
            </Link>
            <Link
              href="/demo"
              className="btn-outline text-lg px-8 py-3"
            >
              Watch Demo
            </Link>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="px-6 py-16 bg-white">
        <div className="mx-auto max-w-7xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Everything you need to study smarter
            </h2>
            <p className="text-gray-600 text-lg">
              From document upload to mastery tracking, Global Brain adapts to your learning style
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Smart Note Organizer */}
            <div className="card card-hover text-center">
              <div className="mx-auto w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                <BookOpen className="h-6 w-6 text-primary-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Smart Note Organizer
              </h3>
              <p className="text-gray-600">
                Upload PDFs, DOCX, presentations, or images. We automatically chunk, 
                summarize, and generate flashcards from your materials.
              </p>
            </div>

            {/* Adaptive Tutor */}
            <div className="card card-hover text-center">
              <div className="mx-auto w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                <MessageCircle className="h-6 w-6 text-primary-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Adaptive Tutor Chat
              </h3>
              <p className="text-gray-600">
                Ask anything with source-grounded answers and inline citations. 
                Adjust reading level from elementary to graduate school.
              </p>
            </div>

            {/* Brain Boost */}
            <div className="card card-hover text-center">
              <div className="mx-auto w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                <Zap className="h-6 w-6 text-primary-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Daily Brain Boost
              </h3>
              <p className="text-gray-600">
                10-minute personalized review sessions with spaced repetition. 
                Build streaks and target your weak areas.
              </p>
            </div>

            {/* Progress Dashboard */}
            <div className="card card-hover text-center">
              <div className="mx-auto w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                <TrendingUp className="h-6 w-6 text-primary-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Progress Dashboard
              </h3>
              <p className="text-gray-600">
                Track topic mastery, study streaks, time saved, and learning gains 
                with detailed analytics.
              </p>
            </div>

            {/* Multi-tenant */}
            <div className="card card-hover text-center">
              <div className="mx-auto w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                <Users className="h-6 w-6 text-primary-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                School Ready
              </h3>
              <p className="text-gray-600">
                Multi-tenant architecture supports individual students and 
                entire schools with privacy controls.
              </p>
            </div>

            {/* Privacy */}
            <div className="card card-hover text-center">
              <div className="mx-auto w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                <Brain className="h-6 w-6 text-primary-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Privacy First
              </h3>
              <p className="text-gray-600">
                COPPA/FERPA compliant with data isolation, export controls, 
                and content filtering for safe learning.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="px-6 py-16 bg-primary-600">
        <div className="mx-auto max-w-4xl text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to transform your studying?
          </h2>
          <p className="text-primary-100 text-lg mb-8">
            Join thousands of students already learning smarter with Global Brain
          </p>
          <Link
            href="/signup"
            className="inline-flex items-center bg-white text-primary-600 font-semibold px-8 py-3 rounded-lg hover:bg-primary-50 transition-colors duration-200"
          >
            Start Free Today
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="px-6 py-8 bg-gray-900 text-gray-400">
        <div className="mx-auto max-w-7xl text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="flex h-6 w-6 items-center justify-center rounded bg-primary-600">
              <Brain className="h-4 w-4 text-white" />
            </div>
            <span className="text-lg font-bold text-white">Global Brain</span>
          </div>
          <p className="text-sm">
            © 2024 Global Brain. All rights reserved. Made with ❤️ for learners everywhere.
          </p>
        </div>
      </footer>
    </div>
  );
}