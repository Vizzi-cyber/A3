/**
 * 从 catch 的 unknown error 中提取可读消息。
 * 如果 error 不是 Error 实例，返回 fallback。
 */
export function extractApiError(error: unknown, fallback = '请求失败'): string {
  return error instanceof Error ? error.message : fallback
}
