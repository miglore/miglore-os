// Miglore OS — API 客户端
// 同源相对路径: dev 由 Vite proxy 转发到 5001, 容器内由 nginx /api 代理到 backend 服务
const API_BASE = '';

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
  evidence_count?: number;
}

export interface ProjectListData {
  projects: Project[];
  stats: { total: number; done: number; tech_stacks: number; milestones: number };
}

export interface EvidenceInterview {
  id: number;
  question: string;
  answer: string;
  skill_name: string | null;
}

export interface Evidence {
  id: number;
  title: string;
  category: string;
  description: string | null;
  technical_detail: string | null;
  result: string | null;
  interview_count: number;
  interviews: EvidenceInterview[];
}

export interface Milestone {
  id: number;
  title: string;
  status: 'done' | 'current' | 'todo';
  sort_order: number;
  achieved_at: string | null;
}

export interface ProjectDetailData {
  project: Project;
  milestones: Milestone[];
  evidence: Evidence[];
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

// ---- Career ----

export interface CareerDirection {
  id: number;
  name: string;
  description: string | null;
  target_role: string | null;
  status: string;
  application_count: number;
}

export interface JobApplication {
  id: number;
  company: string;
  position: string;
  city: string | null;
  salary: string | null;
  channel: string | null;
  status: string;
  applied_at: string | null;
  note: string | null;
  direction_id: number | null;
  direction_name: string | null;
}

export interface Interview {
  id: number;
  application_id: number;
  company: string;
  position: string;
  round: string;
  scheduled_at: string | null;
  interviewer: string | null;
  result: string;
  review: string | null;
}

export interface CareerData {
  directions: CareerDirection[];
  stats: {
    total: number;
    active: number;
    interviewing: number;
    offers: number;
    rejected: number;
    pending_interviews: number;
  };
  recent_applications: JobApplication[];
  upcoming_interviews: Interview[];
  recent_interviews: Interview[];
}

export interface JDAnalyzeResult {
  engine: string;
  total_required: number;
  required: string[];
  matched: string[];
  partial: string[];
  missing: string[];
  score: number;
}
