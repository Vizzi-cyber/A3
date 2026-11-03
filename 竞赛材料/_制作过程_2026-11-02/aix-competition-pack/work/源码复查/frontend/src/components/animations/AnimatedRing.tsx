/**
 * 环形进度动画（AnimatedRing）
 * SVG 圆环从 0 绘制到目标百分比，中央显示数值（可配 CountUp）。
 */
import React, { useEffect, useRef } from "react";
import gsap from "gsap";

interface AnimatedRingProps {
  percent: number;           // 0-100
  size?: number;             // 像素
  strokeWidth?: number;
  color?: string;
  trackColor?: string;
  children?: React.ReactNode; // 中央内容（如数字）
  className?: string;
}

const AnimatedRing: React.FC<AnimatedRingProps> = ({
  percent,
  size = 120,
  strokeWidth = 10,
  color = "#0052ff",
  trackColor = "#eef1f6",
  children,
  className = "",
}) => {
  const circleRef = useRef<SVGCircleElement>(null);
  const wrapRef = useRef<HTMLDivElement>(null);
  const pct = Math.min(100, Math.max(0, percent));
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;

  useEffect(() => {
    const circle = circleRef.current;
    const wrap = wrapRef.current;
    if (!circle || !wrap) return;

    circle.style.strokeDasharray = `${circumference}`;
    circle.style.strokeDashoffset = `${circumference}`;

    import("gsap/ScrollTrigger").then(({ ScrollTrigger }) => {
      gsap.registerPlugin(ScrollTrigger);
      ScrollTrigger.create({
        trigger: wrap,
        start: "top 90%",
        once: true,
        onEnter: () => {
          gsap.to(circle, {
            strokeDashoffset: circumference * (1 - pct / 100),
            duration: 1.5,
            ease: "power2.inOut",
          });
        },
      });
    });
  }, [circumference, pct]);

  return (
    <div ref={wrapRef} className={`relative inline-flex items-center justify-center ${className}`}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={trackColor}
          strokeWidth={strokeWidth}
        />
        <circle
          ref={circleRef}
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        {children}
      </div>
    </div>
  );
};

export default AnimatedRing;
