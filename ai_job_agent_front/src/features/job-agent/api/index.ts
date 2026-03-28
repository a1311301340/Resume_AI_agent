import http, { unwrapData } from "@/shared/api/http";
import type { ProcessMode, TaskItem } from "@/shared/types";

export async function uploadResume(
  file: File,
  onProgress?: (percent: number) => void
): Promise<TaskItem> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await http.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (event) => {
      if (!onProgress || !event.total) return;
      const percent = Math.min(100, Math.round((event.loaded / event.total) * 100));
      onProgress(percent);
    }
  });
  return unwrapData<TaskItem>(res);
}

export async function processTask(payload: {
  task_id: string;
  jd_text?: string;
  mode: ProcessMode;
}): Promise<Record<string, unknown>> {
  const res = await http.post("/process", payload);
  return unwrapData<Record<string, unknown>>(res);
}

export async function getResult(taskId: string): Promise<TaskItem> {
  const res = await http.get(`/result/${taskId}`);
  return unwrapData<TaskItem>(res);
}

export async function exportResult(taskId: string): Promise<{ export_path: string }> {
  const res = await http.get(`/export/${taskId}`);
  return unwrapData<{ export_path: string }>(res);
}

export async function chat(payload: {
  message: string;
  task_id?: string;
  resume_text?: string;
  jd_text?: string;
  history?: Array<Record<string, unknown>>;
}): Promise<{ reply: string }> {
  const res = await http.post("/agent/chat", payload);
  return unwrapData<{ reply: string }>(res);
}

export async function createTaskForPolling(payload: {
  jdText?: string;
  mode: "resume_parse" | "jd_match" | "full_process";
  filePath?: string;
}): Promise<{
  taskId: string;
  status: string;
  progress: number;
  currentStep: string;
  createdAt: string;
  updatedAt: string;
}> {
  const res = await http.post("/task/create", payload);
  return unwrapData(res);
}

export async function getTaskStatus(taskId: string): Promise<{
  taskId: string;
  status: string;
  progress: number;
  currentStep: string;
  createdAt: string;
  updatedAt: string;
}> {
  const res = await http.get(`/task/${taskId}`);
  return unwrapData(res);
}

export async function getHistoryTasks(): Promise<Array<Record<string, unknown>>> {
  const res = await http.get("/history/tasks");
  return unwrapData<Array<Record<string, unknown>>>(res);
}

export async function getHistoryTaskDetail(taskId: string): Promise<Record<string, unknown>> {
  const res = await http.get(`/history/tasks/${taskId}`);
  return unwrapData<Record<string, unknown>>(res);
}

export async function getHistoryTaskChats(taskId: string): Promise<Array<Record<string, unknown>>> {
  const res = await http.get(`/history/tasks/${taskId}/chats`);
  return unwrapData<Array<Record<string, unknown>>>(res);
}

export async function saveHistoryTaskVersion(payload: {
  taskId: string;
  result: Record<string, unknown>;
  note?: string;
  applyAsCurrent?: boolean;
}): Promise<Record<string, unknown>> {
  const res = await http.post(`/history/tasks/${payload.taskId}/versions`, {
    result: payload.result,
    note: payload.note || "",
    apply_as_current: payload.applyAsCurrent ?? true
  });
  return unwrapData<Record<string, unknown>>(res);
}

export async function getHistoryTaskVersions(taskId: string): Promise<Array<Record<string, unknown>>> {
  const res = await http.get(`/history/tasks/${taskId}/versions`);
  return unwrapData<Array<Record<string, unknown>>>(res);
}

export async function getHistoryTaskVersionDetail(taskId: string, versionId: number): Promise<Record<string, unknown>> {
  const res = await http.get(`/history/tasks/${taskId}/versions/${versionId}`);
  return unwrapData<Record<string, unknown>>(res);
}
