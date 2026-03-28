import { createRouter, createWebHistory } from "vue-router";
import AppLayout from "@/app/AppLayout.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      component: AppLayout,
      children: [
        { path: "", name: "dashboard", component: () => import("@/pages/dashboard/DashboardPage.vue") },
        { path: "upload", name: "upload", component: () => import("@/pages/upload/UploadPage.vue") },
        { path: "result", name: "result", component: () => import("@/pages/result/ResultPage.vue") },
        { path: "tasks", name: "tasks", component: () => import("@/pages/tasks/TasksPage.vue") },
        { path: "interview", name: "interview", component: () => import("@/pages/interview/InterviewPage.vue") },
        { path: "history", name: "history", component: () => import("@/pages/history/HistoryPage.vue") }
      ]
    }
  ]
});

export default router;

