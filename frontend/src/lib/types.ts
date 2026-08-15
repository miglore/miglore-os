// Miglore OS — 领域类型（对齐 docs/database.md 与 docs/api.md）

export type TaskType = 'learning' | 'project' | 'daily';
export type TaskStatus = 'todo' | 'in_progress' | 'done' | 'cancelled';

export interface Task {
  id: number;
  type: TaskType;
  title: string;
  status: TaskStatus;
  priority: 1 | 2 | 3;
  due_date: string | null;
  track?: string;
  project?: string;
}

export interface Skill {
  id: number;
  name: string;
  level: number; // 1-5
  target_level: number; // 1-5
  status: 'learning' | 'learned' | 'idle';
}

export interface Project {
  id: number;
  name: string;
  description: string;
  tech_stack: string;
  status: 'planning' | 'active' | 'paused' | 'done' | 'archived';
  progress: number; // 0-100
  featured: boolean;
}

export interface StudyLog {
  id: number;
  log_date: string;
  content: string;
  duration_min: number | null;
  mood: number | null;
}

export interface CareerStat {
  label: string;
  value: number;
}

export interface DashboardData {
  hero: {
    date: string;
    weekday: string;
    streak_days: number;
    career_goal: string;
    active_track: { id: number; title: string; stage: string; progress: number };
  } | null;
  continue_learning: Task[];
  learning_progress: Skill[];
  featured_projects: Project[];
  today_tasks: Task[];
  recent_activity: StudyLog[];
  career_status: CareerStat[];
}
