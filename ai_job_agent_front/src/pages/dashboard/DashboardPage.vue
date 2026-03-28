<template>
  <div>
    <h1 style="margin: 0 0 8px; font-size: 24px; font-weight: 700;">AI 求职助手工作台</h1>
    <p style="margin: 0 0 18px; color: #667085;">快速进入简历上传、岗位分析、结果查看与模拟面试场景。</p>

    <div class="grid-2">
      <el-card class="card">
        <template #header>核心能力</template>
        <el-space wrap>
          <el-tag size="large">简历解析</el-tag>
          <el-tag size="large">JD 匹配</el-tag>
          <el-tag size="large">项目改写</el-tag>
          <el-tag size="large">自我介绍</el-tag>
          <el-tag size="large">模拟面试</el-tag>
        </el-space>
      </el-card>
      <el-card class="card">
        <template #header>推荐入口</template>
        <el-space>
          <el-button type="primary" @click="$router.push('/upload')">开始上传分析</el-button>
          <el-button @click="$router.push('/interview')">进入模拟面试</el-button>
        </el-space>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts"></script>

