<template>
  <div>
    <h1 style="margin: 0 0 8px; font-size: 24px; font-weight: 700;">历史记录</h1>
    <p style="margin: 0 0 18px; color: #667085;">查看上传简历历史、任务结果和模拟面试聊天记录。</p>

    <el-card class="card" style="margin-bottom: 12px;">
      <template #header>加载进度</template>
      <div style="margin-bottom: 8px; color: #667085;">历史列表加载</div>
      <el-progress :percentage="store.ops.loadingHistory ? 70 : 100" :status="store.ops.loadingHistory ? undefined : 'success'" />
      <div style="margin: 12px 0 8px; color: #667085;">历史详情加载</div>
      <el-progress :percentage="store.ops.loadingHistoryDetail ? 70 : 100" :status="store.ops.loadingHistoryDetail ? undefined : 'success'" />
    </el-card>

    <el-card class="card" style="margin-bottom: 12px;">
      <template #header>历史任务列表</template>
      <el-button type="primary" :loading="store.ops.loadingHistory" @click="loadTasks" style="margin-bottom: 12px;">刷新列表</el-button>
      <el-table :data="store.historyTasks" stripe v-loading="store.ops.loadingHistory">
        <el-table-column prop="task_id" label="任务ID" min-width="220" />
        <el-table-column prop="filename" label="文件名" min-width="140" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column prop="resume_text_length" label="简历长度" width="100" />
        <el-table-column prop="updated_at" label="更新时间" min-width="160" />
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-space>
              <el-button size="small" @click="viewDetail(row.task_id)">查看</el-button>
              <el-button size="small" type="primary" @click="useTask(row.task_id, row.filename)">设为当前</el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card v-if="store.activeHistoryDetail" class="card" style="margin-bottom: 12px;" v-loading="store.ops.loadingHistoryDetail">
      <template #header>任务详情</template>
      <div><b>任务ID：</b>{{ store.activeHistoryDetail.task_id }}</div>
      <div style="margin-top: 6px;"><b>文件名：</b>{{ store.activeHistoryDetail.filename }}</div>
      <div style="margin-top: 6px;"><b>状态：</b>{{ store.activeHistoryDetail.status }}</div>
      <div style="margin-top: 6px;"><b>简历文本长度：</b>{{ store.activeHistoryDetail.resume_text_length }}</div>
      <el-divider />
      <div style="margin-bottom: 8px;"><b>简历文本内容：</b></div>
      <el-input :model-value="String(store.activeHistoryDetail.resume_text || '')" type="textarea" :rows="10" readonly />
      <el-divider />
      <div style="margin-bottom: 8px;"><b>任务结果：</b></div>
      <pre style="white-space: pre-wrap; line-height: 1.7;">{{ prettyResult }}</pre>
    </el-card>

    <el-card v-if="store.activeHistoryChats.length" class="card">
      <template #header>模拟面试聊天记录</template>
      <div
        v-for="item in store.activeHistoryChats"
        :key="String(item.id)"
        style="margin-bottom: 10px; padding: 10px 14px; border-radius: 10px;"
        :style="{ background: String(item.role) === 'user' ? '#eaf3ff' : '#f6f6f6' }"
      >
        <div style="font-size: 12px; color: #667085; margin-bottom: 4px;">
          {{ item.role }} · {{ item.created_at }}
        </div>
        <div>{{ item.content }}</div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { useJobAgentStore } from "@/features/job-agent/store/useJobAgentStore";

const store = useJobAgentStore();

const prettyResult = computed(() => {
  const result = store.activeHistoryDetail?.result;
  return result ? JSON.stringify(result, null, 2) : "暂无结果";
});

async function loadTasks() {
  try {
    await store.loadHistoryTasks();
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.message || "加载历史列表失败");
  }
}

async function viewDetail(taskId: string) {
  try {
    await store.loadHistoryDetail(taskId);
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.message || "加载详情失败");
  }
}

function useTask(taskId: string, filename: string) {
  store.useHistoryTask(taskId, filename);
  ElMessage.success("已设置为当前任务，可直接去模拟面试页继续对话");
}

onMounted(async () => {
  await loadTasks();
});
</script>
