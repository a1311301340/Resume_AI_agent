<template>
  <div>
    <h1 style="margin: 0 0 8px; font-size: 24px; font-weight: 700;">模拟面试</h1>
    <p style="margin: 0 0 18px; color: #667085;">自动读取当前上传任务的简历内容进行面试对话。</p>

    <el-card class="card" style="margin-bottom: 12px;">
      <template #header>会话进度</template>
      <div style="margin-bottom: 8px; color: #667085;">上下文加载</div>
      <el-progress :percentage="store.ops.loadingInterviewContext ? 70 : 100" :status="store.ops.loadingInterviewContext ? undefined : 'success'" />
      <div style="margin: 12px 0 8px; color: #667085;">消息发送</div>
      <el-progress :percentage="store.ops.chatting ? 70 : 100" :status="store.ops.chatting ? undefined : 'success'" />
    </el-card>

    <el-card class="card" style="margin-bottom: 12px;">
      <template #header>当前任务上下文</template>
      <div><b>任务ID：</b>{{ store.taskId || "暂无" }}</div>
      <div style="margin-top: 6px;"><b>简历文件：</b>{{ store.fileName || "暂无" }}</div>
      <div style="margin-top: 8px; color: #667085;">
        简历文本长度：{{ store.resumeText ? store.resumeText.length : 0 }}
      </div>
      <el-button style="margin-top: 10px;" :loading="store.ops.loadingInterviewContext" @click="reloadContext">刷新上下文</el-button>
    </el-card>

    <el-card class="card" v-loading="store.ops.loadingInterviewContext">
      <template #header>对话</template>
      <div style="min-height: 220px; margin-bottom: 12px;">
        <div
          v-for="(item, index) in store.chatHistory"
          :key="index"
          style="margin-bottom: 10px; padding: 10px 14px; border-radius: 10px;"
          :style="{ background: item.role === 'user' ? '#eaf3ff' : '#f6f6f6' }"
        >
          {{ item.content }}
        </div>
      </div>
      <div style="display: grid; grid-template-columns: 1fr 100px; gap: 12px;">
        <el-input v-model="message" placeholder="请输入你的问题或回答" @keyup.enter="sendMessage" />
        <el-button type="primary" :loading="store.ops.chatting" @click="sendMessage">发送</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import { useJobAgentStore } from "@/features/job-agent/store/useJobAgentStore";

const store = useJobAgentStore();
const message = ref("");

onMounted(async () => {
  try {
    await store.loadResumeContextForInterview();
  } catch (error: any) {
    ElMessage.warning(error?.response?.data?.message || "加载面试上下文失败");
  }
});

async function reloadContext() {
  try {
    await store.loadResumeContextForInterview();
    ElMessage.success("上下文已刷新");
  } catch (error: any) {
    ElMessage.warning(error?.response?.data?.message || "刷新上下文失败");
  }
}

async function sendMessage() {
  if (!message.value.trim()) {
    return;
  }
  const text = message.value;
  message.value = "";
  try {
    await store.sendChat(text);
  } catch {
    message.value = text;
  }
}
</script>
