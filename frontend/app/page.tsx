'use client'

import { useState } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { 
  Brain, 
  BookOpen, 
  MessageSquare, 
  TrendingUp, 
  Upload, 
  Zap,
  CheckCircle,
  ArrowRight
} from 'lucide-react'

export default function HomePage() {
  const [isHovered, setIsHovered] = useState(false)

  const features = [
    {
      icon: Upload,
      title: 'Smart Note Organizer',
      description: 'Upload PDFs, slides, and notes. We automatically process and organize your materials into searchable, structured content.',
      color: 'bg-blue-500'
    },
    {
      icon: Brain,
      title: 'Adaptive AI Tutor',
      description: 'Chat with an AI tutor that adapts to your learning level and provides source-grounded answers with citations.',
      color: 'bg-purple-500'
    },
    {
      icon: Zap,
      title: 'Daily Brain Boost',
      description: '10-minute personalized review sessions with spaced repetition to reinforce learning and track your progress.',
      color: 'bg-green-500'
    },
    {
      icon: TrendingUp,
      title: 'Progress Dashboard',
      description: 'Track your mastery, streaks, and weak areas with detailed analytics and personalized recommendations.',
      color: 'bg-orange-500'
    }
  ]

  const benefits = [
    'Save hours on note organization',
    'Get instant answers to study questions',
    'Improve retention with spaced repetition',
    'Track learning progress over time',
    'Access your materials anywhere',
    'Personalized learning experience'
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Navigation */}
      <nav className="relative z-10 px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <Brain className="h-8 w-8 text-primary-600" />
            <span className="text-xl font-bold text-gray-900">Global Brain</span>
          </div>
          <div className="hidden md:flex items-center space-x-8">
            <Link href="#features" className="text-gray-600 hover:text-gray-900 transition-colors">
              Features
            </Link>
            <Link href="#pricing" className="text-gray-600 hover:text-gray-900 transition-colors">
              Pricing
            </Link>
            <Link href="/login" className="btn-secondary">
              Sign In
            </Link>
            <Link href="/signup" className="btn-primary">
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative px-6 py-20">
        <div className="max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6">
              Your AI Study Partner
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Organize notes, get personalized tutoring, and track progress — all in minutes a day.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link 
                href="/signup"
                className="btn-primary text-lg px-8 py-4"
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
              >
                Start Learning Free
                <ArrowRight className={`ml-2 h-5 w-5 transition-transform ${isHovered ? 'translate-x-1' : ''}`} />
              </Link>
              <Link href="#demo" className="btn-secondary text-lg px-8 py-4">
                Watch Demo
              </Link>
            </div>
          </motion.div>

          {/* Hero Image/Animation */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1, delay: 0.3 }}
            className="mt-16"
          >
            <div className="relative max-w-4xl mx-auto">
              <div className="card p-8 shadow-2xl">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
                  <div className="space-y-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                      <span className="text-sm text-gray-600">AI Tutor Active</span>
                    </div>
                    <div className="space-y-3">
                      <div className="bg-gray-100 rounded-lg p-3">
                        <p className="text-sm text-gray-700">"Can you explain photosynthesis?"</p>
                      </div>
                      <div className="bg-primary-50 rounded-lg p-3">
                        <p className="text-sm text-gray-700">"Photosynthesis is the process where plants convert light energy into chemical energy..."</p>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div className="bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg p-4 text-white">
                      <h3 className="font-semibold mb-2">Today's Brain Boost</h3>
                      <p className="text-sm opacity-90">5 questions • 10 minutes</p>
                    </div>
                    <div className="bg-green-50 rounded-lg p-4">
                      <h3 className="font-semibold text-green-800 mb-2">Progress</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Biology</span>
                          <span>85%</span>
                        </div>
                        <div className="w-full bg-green-200 rounded-full h-2">
                          <div className="bg-green-500 h-2 rounded-full" style={{ width: '85%' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="px-6 py-20 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Everything you need to study smarter
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              From document organization to personalized tutoring, Global Brain helps you learn more effectively.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="card hover:shadow-lg transition-shadow duration-300"
              >
                <div className={`${feature.color} w-12 h-12 rounded-lg flex items-center justify-center mb-4`}>
                  <feature.icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="px-6 py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
            >
              <h2 className="text-4xl font-bold text-gray-900 mb-6">
                Study smarter, not harder
              </h2>
              <p className="text-xl text-gray-600 mb-8">
                Join thousands of students who are already using Global Brain to improve their learning efficiency and academic performance.
              </p>
              <div className="space-y-4">
                {benefits.map((benefit, index) => (
                  <motion.div
                    key={benefit}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                    viewport={{ once: true }}
                    className="flex items-center space-x-3"
                  >
                    <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
                    <span className="text-gray-700">{benefit}</span>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
              className="relative"
            >
              <div className="card p-8">
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold">Weekly Progress</h3>
                    <span className="text-sm text-gray-500">This week</span>
                  </div>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Study time</span>
                      <span className="font-semibold">12.5 hours</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Topics mastered</span>
                      <span className="font-semibold">8</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Current streak</span>
                      <span className="font-semibold text-green-600">5 days</span>
                    </div>
                  </div>
                  <div className="pt-4 border-t border-gray-200">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-primary-600">+23%</p>
                      <p className="text-sm text-gray-600">Improvement this week</p>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-6 py-20 bg-primary-600">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-4">
            Ready to transform your learning?
          </h2>
          <p className="text-xl text-primary-100 mb-8">
            Join thousands of students who are already studying smarter with Global Brain.
          </p>
          <Link href="/signup" className="bg-white text-primary-600 hover:bg-gray-100 font-semibold py-3 px-8 rounded-lg transition-colors duration-200">
            Start Your Free Trial
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-6 py-12 bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Brain className="h-6 w-6 text-primary-400" />
                <span className="text-lg font-bold">Global Brain</span>
              </div>
              <p className="text-gray-400">
                Your AI study partner for smarter learning.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="#features" className="hover:text-white transition-colors">Features</Link></li>
                <li><Link href="#pricing" className="hover:text-white transition-colors">Pricing</Link></li>
                <li><Link href="/docs" className="hover:text-white transition-colors">Documentation</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/about" className="hover:text-white transition-colors">About</Link></li>
                <li><Link href="/blog" className="hover:text-white transition-colors">Blog</Link></li>
                <li><Link href="/careers" className="hover:text-white transition-colors">Careers</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/help" className="hover:text-white transition-colors">Help Center</Link></li>
                <li><Link href="/contact" className="hover:text-white transition-colors">Contact</Link></li>
                <li><Link href="/privacy" className="hover:text-white transition-colors">Privacy</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Global Brain. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}