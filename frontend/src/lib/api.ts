// Miglore OS — API 客户端 (V1.2: 对接真实后端 127.0.0.1:5001)
const API_BASE = 'http://127.0.0.1:5001';

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers ?? {}) },
    ...options,
  });
  if (!res.ok) {
    let message = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      message = body?.error?.message ?? message;
    } catch {
      /* ignore */
    }
    throw new Error(message);
  }
  return (await res.json()) as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: 'POST', body: JSON.stringify(body) }),
  patch: <T>(path: string, body: unknown) =>
    request<T>(path, { method: 'PATCH', body: JSON.stringify(body) }),
};

export interface Task {
  id: number;
  type: string;
  title: string;
  description: string | null;
  status: 'todo' | 'in_progress' | 'done' | 'cancelled';
  priority: 1 | 2 | 3;
  due_date: string | null;
  track_id: number | null;
  track_name: string | null;
  skill_id: number | null;
  skill_name: string | null;
  project_id: number | null;
  completed_at: string | null;
}

export interface LearningTrack {
  id: number;
  title: string;
  description: string | null;
  status: 'active' | 'paused' | 'completed';
  progress: number;
  sort_order: number;
}

export interface Skill {
  id: number;
  name: string;
  level: number;
  target_level: number;
  status: string;
}

export interface Project {
  id: number;
  name: string;
  description: string | null;
  tech_stack: string | null;
  status: string;
  progress: number;
  featured: boolean;
}

export interface StudyLog {
  id: number;
  log_date: string;
  content: string;
  duration_min: number | null;
  mood: number | null;
}

export interface LearningData {
  tracks: LearningTrack[];
  current: {
    id: number;
    title: string;
    description: string | null;
    stage: string;
    progress: number;
    stats: { done: number; total: number; percent: number };
  } | null;
  progress: { done: number; total: number; percent: number };
  tasks: Task[];
}

export interface DashboardData {
  hero: {
    date: string;
    weekday: string;
    streak_days: number;
    career_goal: string;
    active_track: { id: number; title: string; progress: number };
  } | null;
  continue_learning: Task[];
  learning_progress: Skill[];
  featured_projects: Project[];
  today_tasks: Task[];
  recent_activity: StudyLog[];
  career_status: Record<string, never>;
}
