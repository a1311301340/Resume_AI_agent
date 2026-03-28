<template>
  <div class="layout">
    <aside class="sidebar">
      <div style="padding: 12px 16px 20px; font-size: 20px; font-weight: 700;">AI Job Agent</div>
      <el-menu :default-active="route.path" router class="menu-box" background-color="transparent" text-color="#ffffff" active-text-color="#ffffff">
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/upload">上传分析</el-menu-item>
        <el-menu-item index="/result">结果中心</el-menu-item>
        <el-menu-item index="/tasks">任务中心</el-menu-item>
        <el-menu-item index="/interview">模拟面试</el-menu-item>
        <el-menu-item index="/history">历史记录</el-menu-item>
      </el-menu>
    </aside>
    <div class="content">
      <header class="header">
        <div>
          <div style="font-size: 18px; font-weight: 700;">AI 求职助手系统</div>
          <div style="margin-top: 4px; font-size: 13px; color: #667085;">简历上传 · JD 匹配 · 项目改写 · 模拟面试</div>
        </div>
        <el-tag type="info">Refactor V1</el-tag>
      </header>
      <div style="padding: 0 24px 6px;">
        <el-progress
          :percentage="globalProgress"
          :status="hasRunningOps ? undefined : 'success'"
          :show-text="false"
          :stroke-width="4"
        />
      </div>
      <main class="page">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import { useJobAgentStore } from "@/features/job-agent/store/useJobAgentStore";

const route = useRoute();
const store = useJobAgentStore();

const hasRunningOps = computed(() => {
  const ops = store.ops;
  return (
    ops.uploading ||
    ops.processing ||
    ops.fetchingResult ||
    ops.exporting ||
    ops.loadingHistory ||
    ops.loadingHistoryDetail ||
    ops.loadingInterviewContext ||
    ops.chatting ||
    ops.loadingVersions
  );
});

const globalProgress = computed(() => {
  if (store.ops.uploading) return Math.max(5, store.ops.uploadProgress);
  if (store.ops.processing) return Math.max(10, store.ops.processProgress || store.taskStatus.progress || 10);
  if (store.ops.fetchingResult || store.ops.loadingHistory || store.ops.loadingHistoryDetail || store.ops.loadingInterviewContext || store.ops.chatting || store.ops.loadingVersions || store.ops.exporting) {
    return 70;
  }
  return 100;
});
</script>

<style scoped>
.menu-box {
  border-right: none;
}
</style>
