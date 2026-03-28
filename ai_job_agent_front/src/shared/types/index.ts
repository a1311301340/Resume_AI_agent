export type ProcessMode = "resume_check" | "jd_match" | "project_rewrite" | "intro_generate";

export interface BaseResponse<T = unknown> {
  code: number;
  message: string;
  data: T;
}

export interface TaskItem {
  task_id: string;
  taskId?: string;
  filename: string;
  file_path: string;
  filePath?: string;
  status: string;
  created_at: string;
  createdAt?: string;
  updated_at?: string;
  updatedAt?: string;
  progress?: number;
  current_step?: string;
  currentStep?: string;
  result: Record<string, unknown> | null;
  resume_text_saved?: boolean;
  resume_text_length?: number;
  resume_text_error?: string;
}

export interface ChatRecord {
  role: "user" | "assistant";
  content: string;
}
