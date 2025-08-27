// Global types for the Global Brain application

export interface User {
  id: number;
  email: string;
  first_name?: string;
  last_name?: string;
  role: 'student' | 'teacher' | 'admin';
  is_active: boolean;
  tenant_id?: number;
  created_at: string;
}

export interface Document {
  id: number;
  filename: string;
  original_filename: string;
  status: 'uploading' | 'processing' | 'completed' | 'failed';
  file_size: number;
  total_tokens: number;
  total_chunks: number;
  created_at: string;
}

export interface Flashcard {
  id: number;
  front: string;
  back: string;
  difficulty: string;
  topic?: string;
}

export interface ChatMessage {
  id?: number;
  role: 'user' | 'assistant';
  content: string;
  sources?: SearchResult[];
  citations?: Citation[];
  created_at?: string;
}

export interface Citation {
  number: string;
  document_name: string;
  section_title?: string;
  page_number?: number;
  chunk_id: number;
}

export interface SearchResult {
  chunk_id: number;
  document_id: number;
  document_name: string;
  text: string;
  section_title?: string;
  page_number?: number;
  score: number;
  metadata: Record<string, any>;
}

export interface Quiz {
  id: number;
  title: string;
  description?: string;
  total_questions: number;
  time_limit_minutes: number;
  questions: QuizQuestion[];
}

export interface QuizQuestion {
  id: number;
  type: 'multiple_choice' | 'true_false' | 'short_answer';
  question: string;
  options?: string[];
  correct_answer: string;
  explanation?: string;
  points: number;
}

export interface LearningSession {
  id: number;
  type: 'brain_boost' | 'tutor_chat' | 'flashcard_review';
  started_at: string;
  ended_at?: string;
  score?: number;
  total_questions?: number;
  correct_answers?: number;
}

export interface TopicMastery {
  topic: string;
  mastery_score: number;
  confidence: number;
  last_reviewed?: string;
  review_count: number;
  streak_days: number;
  next_review?: string;
  status: 'strong' | 'good' | 'needs_work';
}

export interface ProgressOverview {
  current_streak: number;
  total_study_time_minutes: number;
  total_documents: number;
  total_flashcards: number;
  brain_boost_sessions_completed: number;
  brain_boost_average_score: number;
  this_week: {
    study_sessions: number;
    study_time_minutes: number;
    brain_boosts_completed: number;
  };
}

export interface WeakArea {
  topic: string;
  mastery_score: number;
  priority: 'high' | 'medium' | 'low';
  last_reviewed?: string;
  recommended_action: string;
}

export interface ActivityRecord {
  id: number;
  type: string;
  started_at: string;
  ended_at?: string;
  duration_minutes: number;
  score?: number;
  questions_answered?: number;
  correct_answers?: number;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface UploadProgress {
  file: File;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  document_id?: number;
  error?: string;
}