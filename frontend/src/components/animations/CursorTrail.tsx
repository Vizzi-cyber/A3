/**
 * 鼠标粒子轨迹（CursorTrail）
 * 光标移动时拖出彩色光点残影，1.5 秒淡出扩散——全站科技感。
 * 纯 DOM + CSS 动画，零依赖，节流 40ms 保证性能。
 */
import React, { useEffect } from "react";

const COLORS = ["#6366f1", "#22d3ee", "#a78bfa", "#f472b6"];

const CursorTrail: React.FC = () => {
  useEffect(() => {
    let last = 0;
    let counter = 0;
    const onMove = (e: MouseEvent) => {
      const now = Date.now();
      if (now - last < 40) return;
      last = now;
      const dot = document.createElement("div");
      dot.className = "cursor-trail-dot";
      dot.style.left = `${e.clientX}px`;
      dot.style.top = `${e.clientY}px`;
      dot.style.background = COLORS[counter % COLORS.length];
      dot.style.boxShadow = `0 0 8px ${COLORS[counter % COLORS.length]}99`;
      counter++;
      document.body.appendChild(dot);
      setTimeout(() => dot.remove(), 1500);
    };
    window.addEventListener("mousemove", onMove, { passive: true });
    return () => window.removeEventListener("mousemove", onMove);
  }, []);

  return null;
};

export default CursorTrail;
