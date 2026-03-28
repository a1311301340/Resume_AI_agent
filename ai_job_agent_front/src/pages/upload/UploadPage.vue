<template>
  <div>
    <h1 style="margin: 0 0 8px; font-size: 24px; font-weight: 700;">上传与任务发起</h1>
    <p style="margin: 0 0 18px; color: #667085;">上传简历、填写岗位 JD，并快速发起分析任务。</p>

    <el-card class="card" style="margin-bottom: 12px;">
      <template #header>流程进度</template>
      <div style="margin-bottom: 8px; color: #667085;">上传进度</div>
      <el-progress :percentage="store.ops.uploadProgress" :status="store.ops.uploading ? undefined : 'success'" />
      <div style="margin: 12px 0 8px; color: #667085;">任务处理进度</div>
      <el-progress :percentage="store.ops.processProgress || store.taskStatus.progress" :status="store.taskStatus.status === 'failed' ? 'exception' : undefined" />
      <div style="margin-top: 8px; color: #667085;">
        {{ store.taskStatus.currentStep || "等待任务启动" }}
      </div>
    </el-card>

    <div class="grid-2">
      <el-card class="card">
        <template #header>上传简历</template>
        <el-upload
          :auto-upload="false"
          :show-file-list="true"
          :on-change="onFileChange"
          :limit="1"
          accept=".pdf,.doc,.docx"
        >
          <el-button type="primary">选择简历文件</el-button>
        </el-upload>
        <div style="margin-top: 12px;">
          <el-button type="success" :loading="store.ops.uploading" :disabled="!selectedFile || store.ops.uploading" @click="submitUpload">
            上传并创建任务
          </el-button>
          <span style="margin-left: 10px; color: #667085;">{{ store.fileName }}</span>
        </div>
      </el-card>

      <el-card class="card">
        <template #header>岗位 JD</template>
        <el-input
          v-model="jdText"
          type="textarea"
          :rows="12"
          placeholder="请输入目标岗位 JD"
        />
        <div style="margin-top: 12px;">
          <el-button type="primary" @click="saveJd">保存 JD</el-button>
          <el-button type="success" :loading="store.ops.processing" :disabled="!store.taskId || store.ops.processing" @click="runMatch">开始匹配</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { ElMessage } from "element-plus";

import { useJobAgentStore } from "@/features/job-agent/store/useJobAgentStore";

const store = useJobAgentStore();
const selectedFile = ref<File | null>(null);
const jdText = ref(store.jdText);

function onFileChange(file: { raw?: File }) {
  const raw = file.raw || null;
  if (!raw) {
    selectedFile.value = null;
    return;
  }

  const ext = raw.name.includes(".") ? raw.name.slice(raw.name.lastIndexOf(".")).toLowerCase() : "";
  if (![".pdf", ".doc", ".docx"].includes(ext)) {
    ElMessage.warning("仅支持 .pdf/.doc/.docx 简历文件");
    selectedFile.value = null;
    return;
  }

  const maxBytes = 10 * 1024 * 1024;
  if (raw.size > maxBytes) {
    ElMessage.warning("文件大小不能超过 10MB");
    selectedFile.value = null;
    return;
  }
  selectedFile.value = raw;
}

async function submitUpload() {
  if (!selectedFile.value) {
    return;
  }
  try {
    const task = await store.upload(selectedFile.value);
    ElMessage.success(`上传成功，任务ID：${task.task_id}`);
    if (task.resume_text_saved === false) {
      ElMessage.warning("文件已上传，但简历文本入库失败，请检查数据库连接");
    }
    if ((task.resume_text_length || 0) === 0) {
      ElMessage.warning("简历文本未解析到内容，建议重试 PDF/DOCX，或确认本机已安装 Word/LibreOffice 以支持 DOC 解析");
    }
  } catch (error: any) {
    const msg = error?.response?.data?.message || "上传失败，请检查后端服务和文件格式";
    ElMessage.error(msg);
  }
}

function saveJd() {
  store.setJdText(jdText.value);
  ElMessage.success("JD 已保存");
}

async function runMatch() {
  store.setJdText(jdText.value);
  if (!jdText.value.trim()) {
    ElMessage.warning("请先填写岗位 JD");
    return;
  }
  if (!store.taskId) {
    ElMessage.warning("请先上传简历");
    return;
  }
  try {
    await store.runProcess("jd_match");
    ElMessage.success("匹配完成，请前往结果页查看");
  } catch (error: any) {
    const msg =
      error?.response?.data?.message ||
      error?.response?.data?.detail ||
      "匹配失败，请根据提示修正后重试";
    ElMessage.error(msg);
  }
}

</script>
