import axios from "axios";
import { ElMessage } from "element-plus";

const http = axios.create({
  baseURL: import.meta.env.VITE_BASE_URL,
  timeout: 20000
});

http.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const data = error?.response?.data;
    const detail = data?.detail;
    let msg = data?.message;
    if (!msg && typeof detail === "string") {
      msg = detail;
    }
    if (!msg && Array.isArray(detail) && detail.length > 0) {
      const first = detail[0];
      if (first?.msg) {
        msg = first.msg;
      }
    }
    ElMessage.error(msg || "请求失败，请稍后重试");
    return Promise.reject(error);
  }
);

export function unwrapData<T>(payload: unknown): T {
  const maybe = payload as { code?: number; data?: T };
  if (typeof maybe === "object" && maybe !== null && "code" in maybe && "data" in maybe) {
    return maybe.data as T;
  }
  return payload as T;
}

export default http;
