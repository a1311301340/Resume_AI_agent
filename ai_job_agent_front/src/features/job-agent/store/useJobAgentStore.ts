import { defineStore } from "pinia";

import {
  chat,
  createTaskForPolling,
  exportResult,
  getHistoryTaskChats,
  getHistoryTaskDetail,
  getHistoryTasks,
  getHistoryTaskVersionDetail,
  getHistoryTaskVersions,
  getResult,
  getTaskStatus,
  processTask,
  saveHistoryTaskVersion,
  uploadResume
} from "@/features/job-agent/api";
import type { ChatRecord, ProcessMode, TaskItem } from "@/shared/types";

interface TaskStatusState {
  taskId: string;
  status: string;
  progress: number;
  currentStep: string;
  createdAt: string;
  updatedAt: string;
}

interface OpsState {
  uploading: boolean;
  uploadProgress: number;
  processing: boolean;
  processProgress: number;
  fetchingResult: boolean;
  exporting: boolean;
  loadingHistory: boolean;
  loadingHistoryDetail: boolean;
  loadingInterviewContext: boolean;
  chatting: boolean;
  loadingVersions: boolean;
}

let timer: number | null = null;

export const useJobAgentStore = defineStore("jobAgent", {
  state: () => ({
    fileName: localStorage.getItem("ja_fileName") || "",
    taskId: localStorage.getItem("ja_taskId") || "",
    filePath: localStorage.getItem("ja_filePath") || "",
    jdText: localStorage.getItem("ja_jdText") || "",
    result: null as Record<string, unknown> | null,
    task: null as TaskItem | null,
    taskStatus: {
      taskId: "",
      status: "idle",
      progress: 0,
      currentStep: "等待任务启动",
      createdAt: "",
      updatedAt: ""
    } as TaskStatusState,
    chatHistory: [] as ChatRecord[],
    resumeText: "",
    historyTasks: [] as Array<Record<string, unknown>>,
    activeHistoryDetail: null as Record<string, unknown> | null,
    activeHistoryChats: [] as Array<Record<string, unknown>>,
    resultVersions: [] as Array<Record<string, unknown>>,
    ops: {
      uploading: false,
      uploadProgress: 0,
      processing: false,
      processProgress: 0,
      fetchingResult: false,
      exporting: false,
      loadingHistory: false,
      loadingHistoryDetail: false,
      loadingInterviewContext: false,
      chatting: false,
      loadingVersions: false
    } as OpsState
  }),
  actions: {
    _persistBase() {
      localStorage.setItem("ja_fileName", this.fileName || "");
      localStorage.setItem("ja_taskId", this.taskId || "");
      localStorage.setItem("ja_filePath", this.filePath || "");
      localStorage.setItem("ja_jdText", this.jdText || "");
    },
    _syncProcessFromTaskStatus() {
      const p = Number(this.taskStatus.progress || 0);
      this.ops.processProgress = Math.max(this.ops.processProgress, p);
      this.ops.processing = this.taskStatus.status === "running";
    },
    async upload(file: File) {
      this.ops.uploading = true;
      this.ops.uploadProgress = 0;
      try {
        const task = await uploadResume(file, (percent) => {
          this.ops.uploadProgress = percent;
        });
        this.fileName = task.filename;
        this.taskId = task.task_id;
        this.filePath = task.file_path;
        this.task = task;
        this._persistBase();
        this.taskStatus = {
          taskId: task.task_id,
          status: "pending",
          progress: task.progress ?? 5,
          currentStep: task.current_step ?? "文件已上传，等待处理",
          createdAt: task.created_at,
          updatedAt: task.updated_at ?? task.created_at
        };
        this.ops.uploadProgress = Math.max(this.ops.uploadProgress, 100);
        return task;
      } finally {
        this.ops.uploading = false;
      }
    },
    setJdText(text: string) {
      this.jdText = text;
      this._persistBase();
    },
    async runProcess(mode: ProcessMode) {
      if (!this.taskId) {
        return null;
      }
      this.ops.processing = true;
      this.ops.processProgress = Math.max(this.ops.processProgress, 15);
      this.taskStatus.status = "running";
      this.taskStatus.currentStep = "正在处理任务";
      this.taskStatus.progress = Math.max(this.taskStatus.progress || 0, 15);
      try {
        const res = await processTask({
          task_id: this.taskId,
          jd_text: this.jdText,
          mode
        });
        this.result = res;
        this.ops.processProgress = 95;
        await this.pollTaskStatus();
        this.ops.processProgress = Math.max(this.ops.processProgress, 100);
        return res;
      } catch (error) {
        this.taskStatus.status = "failed";
        this.taskStatus.currentStep = "处理失败";
        this.taskStatus.progress = Math.max(this.taskStatus.progress || 0, this.ops.processProgress || 0);
        throw error;
      } finally {
        this.ops.processing = false;
      }
    },
    async fetchResult() {
      if (!this.taskId) {
        return null;
      }
      this.ops.fetchingResult = true;
      try {
        const task = await getResult(this.taskId);
        this.task = task;
        this.result = task.result || null;
        return task;
      } finally {
        this.ops.fetchingResult = false;
      }
    },
    async runExport() {
      if (!this.taskId) {
        return null;
      }
      this.ops.exporting = true;
      try {
        return await exportResult(this.taskId);
      } finally {
        this.ops.exporting = false;
      }
    },
    async sendChat(message: string) {
      if (!message.trim()) {
        return;
      }
      this.chatHistory.push({ role: "user", content: message });
      this.ops.chatting = true;
      try {
        const res = await chat({
          message,
          task_id: this.taskId,
          jd_text: this.jdText,
          history: this.chatHistory
        });
        this.chatHistory.push({ role: "assistant", content: res.reply });
      } finally {
        this.ops.chatting = false;
      }
    },
    async startTaskCenterFlow() {
      this.ops.processing = true;
      this.ops.processProgress = Math.max(this.ops.processProgress, 10);
      try {
        const task = await createTaskForPolling({
          jdText: this.jdText,
          mode: "jd_match",
          filePath: this.filePath
        });
        this.taskStatus = task;
        this.taskId = task.taskId;
        this._persistBase();
        this._syncProcessFromTaskStatus();
      } finally {
        this.ops.processing = false;
      }
    },
    async pollTaskStatus() {
      if (!this.taskId) {
        return;
      }
      const task = await getTaskStatus(this.taskId);
      this.taskStatus = task;
      this._syncProcessFromTaskStatus();
      if (["success", "failed"].includes(task.status)) {
        this.stopPolling();
        this.ops.processing = false;
        if (task.status === "success") {
          this.ops.processProgress = 100;
        }
      }
    },
    async loadHistoryTasks() {
      this.ops.loadingHistory = true;
      try {
        const tasks = await getHistoryTasks();
        this.historyTasks = tasks;
        return tasks;
      } finally {
        this.ops.loadingHistory = false;
      }
    },
    async loadHistoryDetail(taskId: string) {
      this.ops.loadingHistoryDetail = true;
      try {
        const detail = await getHistoryTaskDetail(taskId);
        const chats = await getHistoryTaskChats(taskId);
        this.activeHistoryDetail = detail;
        this.activeHistoryChats = chats;
        return { detail, chats };
      } finally {
        this.ops.loadingHistoryDetail = false;
      }
    },
    async loadResultVersions(taskId?: string) {
      const targetTaskId = taskId || this.taskId;
      if (!targetTaskId) return [];
      this.ops.loadingVersions = true;
      try {
        const versions = await getHistoryTaskVersions(targetTaskId);
        this.resultVersions = versions;
        return versions;
      } finally {
        this.ops.loadingVersions = false;
      }
    },
    async saveCurrentResultVersion(note = "") {
      if (!this.taskId || !this.result) return null;
      this.ops.loadingVersions = true;
      try {
        const payload = await saveHistoryTaskVersion({
          taskId: this.taskId,
          result: this.result,
          note,
          applyAsCurrent: true
        });
        await this.loadResultVersions(this.taskId);
        return payload;
      } finally {
        this.ops.loadingVersions = false;
      }
    },
    async loadVersionAsCurrent(versionId: number) {
      if (!this.taskId) return null;
      this.ops.loadingVersions = true;
      try {
        const detail = await getHistoryTaskVersionDetail(this.taskId, versionId);
        const result = (detail.result || {}) as Record<string, unknown>;
        this.result = result;
        await saveHistoryTaskVersion({
          taskId: this.taskId,
          result,
          note: `回滚到版本 #${detail.version_no || versionId}`,
          applyAsCurrent: true
        });
        await this.loadResultVersions(this.taskId);
        return detail;
      } finally {
        this.ops.loadingVersions = false;
      }
    },
    useHistoryTask(taskId: string, filename = "") {
      this.taskId = taskId;
      this.fileName = filename;
      this._persistBase();
    },
    async loadResumeContextForInterview() {
      this.ops.loadingInterviewContext = true;
      try {
        if (!this.taskId) {
          const tasks = await this.loadHistoryTasks();
          if (tasks.length > 0) {
            const first = tasks[0] as Record<string, unknown>;
            const taskId = String(first.task_id || "");
            if (taskId) {
              this.taskId = taskId;
              this.fileName = String(first.filename || "");
              this._persistBase();
            }
          }
        }

        if (!this.taskId) {
          return null;
        }

        const detail = await getHistoryTaskDetail(this.taskId);
        const chats = await getHistoryTaskChats(this.taskId);
        this.resumeText = String(detail.resume_text || "");
        this.activeHistoryDetail = detail;
        this.activeHistoryChats = chats;
        this.chatHistory = chats.map((item) => ({
          role: String(item.role || "assistant") as "user" | "assistant",
          content: String(item.content || "")
        }));
        return detail;
      } finally {
        this.ops.loadingInterviewContext = false;
      }
    },
    startPolling() {
      this.stopPolling();
      this.ops.processing = true;
      timer = window.setInterval(() => {
        this.pollTaskStatus().catch(() => {
          this.ops.processing = false;
          this.stopPolling();
        });
      }, 2500);
    },
    stopPolling() {
      if (timer) {
        window.clearInterval(timer);
        timer = null;
      }
      if (this.taskStatus.status !== "running") {
        this.ops.processing = false;
      }
    }
  }
});
