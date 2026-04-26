import { useEffect, useRef } from 'react'

/**
 * 追踪页面/组件停留时长（秒）。
 * @param resetDeps  依赖变化时重置计时器
 * @param minSeconds 最小返回值（默认 30，防止秒刷）
 * @returns () => number  调用时返回当前已停留秒数
 */
export function useElapsedTime(resetDeps: React.DependencyList = [], minSeconds = 30): () => number {
  const startRef = useRef<number>(Date.now())

  useEffect(() => {
    startRef.current = Date.now()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, resetDeps)

  return () => Math.max(minSeconds, Math.round((Date.now() - startRef.current) / 1000))
}
