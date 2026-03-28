<template>
  <div>
    <h1 style="margin: 0 0 8px; font-size: 24px; font-weight: 700;">结果中心</h1>
    <p style="margin: 0 0 18px; color: #667085;">结构化展示匹配分析，并支持字段化编辑与版本保存。</p>

    <el-card class="card" style="margin-bottom: 12px;">
      <template #header>加载进度</template>
      <div style="margin-bottom: 8px; color: #667085;">结果加载</div>
      <el-progress :percentage="store.ops.fetchingResult ? 70 : 100" :status="store.ops.fetchingResult ? undefined : 'success'" />
      <div style="margin: 12px 0 8px; color: #667085;">版本加载</div>
      <el-progress :percentage="store.ops.loadingVersions ? 70 : 100" :status="store.ops.loadingVersions ? undefined : 'success'" />
      <div style="margin: 12px 0 8px; color: #667085;">导出进度</div>
      <el-progress :percentage="store.ops.exporting ? 70 : 100" :status="store.ops.exporting ? undefined : 'success'" />
    </el-card>

    <el-card class="card" style="margin-bottom: 12px;">
      <template #header>任务概览</template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="任务ID">{{ store.taskId || "-" }}</el-descriptions-item>
        <el-descriptions-item label="简历文件">{{ store.fileName || "-" }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ store.task?.status || "-" }}</el-descriptions-item>
        <el-descriptions-item label="JD 关键词数">{{ jdKeywords.length }}</el-descriptions-item>
      </el-descriptions>
      <el-space style="margin-top: 12px;">
        <el-button type="primary" :loading="store.ops.fetchingResult" @click="refreshResult">刷新结果</el-button>
        <el-button :loading="store.ops.exporting" @click="downloadResult">导出 TXT</el-button>
      </el-space>
      <div v-if="exportPath" style="margin-top: 10px; color: #409eff;">导出路径：{{ exportPath }}</div>
    </el-card>

    <div class="grid-2">
      <el-card class="card" v-loading="store.ops.fetchingResult">
        <template #header>匹配得分</template>
        <div style="display: flex; align-items: center; gap: 18px;">
          <el-progress type="dashboard" :percentage="score" :stroke-width="12" />
          <div>
            <div style="font-size: 32px; font-weight: 700;">{{ score }} 分</div>
            <div style="margin-top: 8px; color: #667085;">{{ summaryText }}</div>
          </div>
        </div>
      </el-card>

      <el-card class="card" v-loading="store.ops.fetchingResult">
        <template #header>关键词分析</template>
        <div style="margin-bottom: 8px; font-weight: 600;">JD 关键词</div>
        <el-space wrap>
          <el-tag v-for="item in jdKeywords" :key="item" type="info">{{ item }}</el-tag>
        </el-space>
        <el-divider />
        <div style="margin-bottom: 8px; font-weight: 600;">匹配命中</div>
        <el-space wrap>
          <el-tag v-for="item in matchedSkills" :key="item" type="success">{{ item }}</el-tag>
        </el-space>
        <el-divider />
        <div style="margin-bottom: 8px; font-weight: 600;">缺失项</div>
        <el-space wrap>
          <el-tag v-for="item in missingSkills" :key="item" type="danger">{{ item }}</el-tag>
        </el-space>
      </el-card>
    </div>

    <div class="grid-2" style="margin-top: 12px;">
      <el-card class="card" v-loading="store.ops.fetchingResult">
        <template #header>项目改写建议</template>
        <el-timeline>
          <el-timeline-item v-for="(item, idx) in rewrittenProjects" :key="idx" :timestamp="`建议 ${idx + 1}`">
            {{ item }}
          </el-timeline-item>
        </el-timeline>
      </el-card>

      <el-card class="card" v-loading="store.ops.fetchingResult">
        <template #header>推荐动作</template>
        <el-timeline>
          <el-timeline-item v-for="(item, idx) in recommendations" :key="idx" :timestamp="`动作 ${idx + 1}`">
            {{ item }}
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </div>

    <el-card class="card" style="margin-top: 12px;" v-loading="store.ops.fetchingResult">
      <template #header>面试自我介绍（建议稿）</template>
      <el-input :model-value="introText" type="textarea" :rows="5" readonly />
    </el-card>

    <el-card class="card" style="margin-top: 12px;" v-loading="store.ops.fetchingResult">
      <template #header>简历预览（系统抽取）</template>
      <div style="margin-bottom: 8px; font-weight: 600;">技能片段</div>
      <el-space wrap>
        <el-tag v-for="item in resumeSkills" :key="item">{{ item }}</el-tag>
      </el-space>
      <el-divider />
      <div style="margin-bottom: 8px; font-weight: 600;">项目片段</div>
      <el-timeline>
        <el-timeline-item v-for="(item, idx) in resumeProjects" :key="idx" :timestamp="`项目 ${idx + 1}`">
          {{ item }}
        </el-timeline-item>
      </el-timeline>
    </el-card>

    <el-card class="card" style="margin-top: 12px;">
      <template #header>结果编辑器（字段化）</template>
      <el-form label-width="110px">
        <div class="grid-2">
          <el-form-item label="匹配得分">
            <el-input-number v-model="editForm.score" :min="0" :max="100" />
          </el-form-item>
          <el-form-item label="匹配摘要">
            <el-input v-model="editForm.summary" />
          </el-form-item>
        </div>
        <el-form-item label="JD关键词">
          <el-input v-model="editForm.jdKeywordsText" placeholder="逗号分隔，例如：Python, FastAPI, SQL" />
        </el-form-item>
        <el-form-item label="命中技能">
          <el-input v-model="editForm.matchedSkillsText" placeholder="逗号分隔" />
        </el-form-item>
        <el-form-item label="缺失技能">
          <el-input v-model="editForm.missingSkillsText" placeholder="逗号分隔" />
        </el-form-item>
        <el-form-item label="推荐动作">
          <el-input v-model="editForm.recommendationsText" type="textarea" :rows="4" placeholder="每行一条" />
        </el-form-item>
        <el-form-item label="项目改写">
          <el-input v-model="editForm.rewrittenProjectsText" type="textarea" :rows="5" placeholder="每行一条" />
        </el-form-item>
        <el-form-item label="自我介绍">
          <el-input v-model="editForm.intro" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <el-space>
        <el-button type="primary" @click="applyFormToResult">应用表单到结果</el-button>
        <el-button @click="syncFormFromResult">从当前结果重载</el-button>
      </el-space>
    </el-card>

    <el-card class="card" style="margin-top: 12px;">
      <template #header>结果版本管理</template>
      <el-space style="margin-bottom: 10px;">
        <el-button v-if="!isEditing" type="primary" @click="startEditJson">进入 JSON 编辑</el-button>
        <el-button v-if="isEditing" @click="cancelEditJson">取消 JSON 编辑</el-button>
        <el-button v-if="isEditing" type="success" @click="applyEditedJsonResult">应用 JSON 到结果</el-button>
      </el-space>
      <el-input
        v-model="editableResultJson"
        type="textarea"
        :rows="12"
        :readonly="!isEditing"
      />
      <el-divider />
      <el-input v-model="versionNote" placeholder="版本备注（可选）" style="max-width: 420px;" />
      <el-space style="margin-top: 10px;">
        <el-button type="primary" :loading="store.ops.loadingVersions" @click="saveCurrentAsVersion">保存为历史版本</el-button>
        <el-button :loading="store.ops.loadingVersions" @click="loadVersions">刷新版本列表</el-button>
      </el-space>
      <el-table :data="store.resultVersions" style="margin-top: 12px;" stripe v-loading="store.ops.loadingVersions">
        <el-table-column prop="version_no" label="版本号" width="90" />
        <el-table-column prop="note" label="备注" min-width="220" />
        <el-table-column prop="created_at" label="创建时间" min-width="160" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" :loading="store.ops.loadingVersions" @click="loadVersion(row.id)">加载</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-collapse style="margin-top: 12px;">
      <el-collapse-item title="原始 JSON（调试）" name="1">
        <pre style="white-space: pre-wrap; line-height: 1.7;">{{ prettyResult }}</pre>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";

import { useJobAgentStore } from "@/features/job-agent/store/useJobAgentStore";

const store = useJobAgentStore();
const exportPath = ref("");
const isEditing = ref(false);
const editableResultJson = ref("");
const versionNote = ref("");

const editForm = reactive({
  score: 0,
  summary: "",
  jdKeywordsText: "",
  matchedSkillsText: "",
  missingSkillsText: "",
  recommendationsText: "",
  rewrittenProjectsText: "",
  intro: ""
});

const resultRoot = computed(() => (store.result || {}) as Record<string, any>);
const matchData = computed(() => (resultRoot.value.match || resultRoot.value) as Record<string, any>);
const score = computed(() => Number(matchData.value.score || 0));
const summaryText = computed(() => String(matchData.value.summary || resultRoot.value.summary || "暂无匹配摘要"));

const jdKeywords = computed(() => {
  const fromMatch = matchData.value.jd_keywords;
  const fromPreview = resultRoot.value?.jd_preview?.keywords;
  if (Array.isArray(fromMatch)) return fromMatch.map(String);
  if (Array.isArray(fromPreview)) return fromPreview.map(String);
  return [];
});

const matchedSkills = computed(() => {
  const arr = matchData.value.matched_skills;
  return Array.isArray(arr) ? arr.map(String) : [];
});

const missingSkills = computed(() => {
  const arr = matchData.value.missing_skills;
  return Array.isArray(arr) ? arr.map(String) : [];
});

const rewrittenProjects = computed(() => {
  const arr = resultRoot.value.rewritten_projects;
  return Array.isArray(arr) ? arr.map(String) : [];
});

const recommendations = computed(() => {
  const arr = matchData.value.recommendations;
  return Array.isArray(arr) ? arr.map(String) : [];
});

const introText = computed(() => String(resultRoot.value.intro || "暂无"));

const resumeSkills = computed(() => {
  const arr = resultRoot.value?.resume_preview?.skills;
  return Array.isArray(arr) ? arr.map(String) : [];
});

const resumeProjects = computed(() => {
  const arr = resultRoot.value?.resume_preview?.projects;
  return Array.isArray(arr) ? arr.map(String) : [];
});

const prettyResult = computed(() => {
  return store.result ? JSON.stringify(store.result, null, 2) : "暂无结果";
});

function listToText(list: string[]) {
  return list.join(", ");
}

function textToList(text: string) {
  return text
    .split(/[\n,，]/g)
    .map((s) => s.trim())
    .filter(Boolean);
}

function linesToList(text: string) {
  return text
    .split(/\n/g)
    .map((s) => s.trim())
    .filter(Boolean);
}

function syncEditableFromResult() {
  editableResultJson.value = JSON.stringify(store.result || {}, null, 2);
}

function syncFormFromResult() {
  editForm.score = Number(matchData.value.score || 0);
  editForm.summary = String(matchData.value.summary || "");
  editForm.jdKeywordsText = listToText(jdKeywords.value);
  editForm.matchedSkillsText = listToText(matchedSkills.value);
  editForm.missingSkillsText = listToText(missingSkills.value);
  editForm.recommendationsText = recommendations.value.join("\n");
  editForm.rewrittenProjectsText = rewrittenProjects.value.join("\n");
  editForm.intro = String(resultRoot.value.intro || "");
}

function applyFormToResult() {
  const current = (store.result || {}) as Record<string, any>;
  const next: Record<string, any> = { ...current };
  const match = { ...(next.match || {}) };

  match.score = Number(editForm.score || 0);
  match.summary = editForm.summary;
  match.jd_keywords = textToList(editForm.jdKeywordsText);
  match.matched_skills = textToList(editForm.matchedSkillsText);
  match.missing_skills = textToList(editForm.missingSkillsText);
  match.recommendations = linesToList(editForm.recommendationsText);

  next.match = match;
  next.intro = editForm.intro;
  next.rewritten_projects = linesToList(editForm.rewrittenProjectsText);
  next.jd_preview = {
    ...(next.jd_preview || {}),
    keywords: textToList(editForm.jdKeywordsText)
  };

  store.result = next;
  syncEditableFromResult();
  ElMessage.success("字段化编辑已应用到当前结果");
}

function startEditJson() {
  isEditing.value = true;
  syncEditableFromResult();
}

function cancelEditJson() {
  isEditing.value = false;
  syncEditableFromResult();
}

function applyEditedJsonResult() {
  try {
    const parsed = JSON.parse(editableResultJson.value || "{}");
    store.result = parsed;
    syncFormFromResult();
    ElMessage.success("JSON 编辑已应用到当前结果");
  } catch {
    ElMessage.error("JSON 格式错误，无法应用");
  }
}

async function saveCurrentAsVersion() {
  if (!store.taskId) {
    ElMessage.warning("暂无任务");
    return;
  }
  if (isEditing.value) {
    try {
      store.result = JSON.parse(editableResultJson.value || "{}");
    } catch {
      ElMessage.error("JSON 格式错误，无法保存版本");
      return;
    }
  }
  try {
    await store.saveCurrentResultVersion(versionNote.value.trim());
    versionNote.value = "";
    ElMessage.success("已保存历史版本");
  } catch {
    ElMessage.error("保存历史版本失败");
  }
}

async function loadVersions() {
  try {
    await store.loadResultVersions();
  } catch {
    ElMessage.error("加载版本列表失败");
  }
}

async function loadVersion(versionId: number) {
  try {
    await store.loadVersionAsCurrent(versionId);
    syncEditableFromResult();
    syncFormFromResult();
    ElMessage.success("已加载并应用该版本");
  } catch {
    ElMessage.error("加载版本失败");
  }
}

async function refreshResult() {
  if (!store.taskId) {
    ElMessage.warning("暂无任务");
    return;
  }
  try {
    await store.fetchResult();
    syncEditableFromResult();
    syncFormFromResult();
    await loadVersions();
    ElMessage.success("结果已刷新");
  } catch {
    ElMessage.error("加载结果失败");
  }
}

async function downloadResult() {
  if (!store.taskId) {
    ElMessage.warning("暂无任务");
    return;
  }
  try {
    const data = await store.runExport();
    exportPath.value = data?.export_path || "";
    ElMessage.success("导出完成");
  } catch {
    ElMessage.error("导出失败");
  }
}

onMounted(async () => {
  if (store.taskId && !store.result) {
    await refreshResult();
  } else {
    syncEditableFromResult();
    syncFormFromResult();
    await loadVersions();
  }
});
</script>
