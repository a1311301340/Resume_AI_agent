<template>
  <div>
    <h1 style="margin: 0 0 8px; font-size: 24px; font-weight: 700;">任务中心</h1>
    <p style="margin: 0 0 18px; color: #667085;">查看当前任务状态、处理进度与执行步骤。</p>

    <el-card class="card">
      <template #header>任务处理进度</template>
      <div style="margin-bottom: 8px; color: #667085;">任务状态进度</div>
      <el-progress :percentage="store.taskStatus.progress" :stroke-width="16" :status="store.taskStatus.status === 'failed' ? 'exception' : undefined" />
      <div style="margin: 12px 0 8px; color: #667085;">当前执行进度</div>
      <el-progress :percentage="store.ops.processProgress || store.taskStatus.progress" :stroke-width="12" :status="store.ops.processing ? undefined : 'success'" />
      <div style="margin-top: 12px; display: flex; justify-content: space-between; gap: 8px; flex-wrap: wrap; color: #667085;">
        <span>当前状态：{{ store.taskStatus.status }}</span>
        <span>当前步骤：{{ store.taskStatus.currentStep }}</span>
      </div>
      <div style="margin-top: 12px;">
        <el-button type="primary" :loading="store.ops.processing" @click="refresh">刷新状态</el-button>
        <el-button @click="startPolling">开始轮询</el-button>
        <el-button @click="stopPolling">停止轮询</el-button>
      </div>
    </el-card>

    <el-card class="card" style="margin-top: 16px;">
      <template #header>任务信息</template>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="任务编号">{{ store.taskStatus.taskId || "-" }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ store.taskStatus.createdAt || "-" }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ store.taskStatus.updatedAt || "-" }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import { useJobAgentStore } from "@/features/job-agent/store/useJobAgentStore";

const store = useJobAgentStore();

async function refresh() {
  if (!store.taskId) {
    ElMessage.warning("暂无任务");
    return;
  }
  try {
    await store.pollTaskStatus();
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.message || "刷新任务状态失败");
  }
}

function startPolling() {
  store.startPolling();
}

function stopPolling() {
  store.stopPolling();
}
</script>
