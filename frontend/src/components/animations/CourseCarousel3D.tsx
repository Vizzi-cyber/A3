/**
 * 3D 环形轮播（CourseCarousel3D）
 * 课程卡片以 3D 环形排列，支持：
 *   - 自动轮播（间隔切换）
 *   - 点击卡片 / 左右箭头切换
 *   - 鼠标悬停暂停
 * 纯 CSS 3D transform + GSAP，无新依赖。
 */
import React, { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { LeftOutlined, RightOutlined } from "@ant-design/icons";

export interface CarouselItem {
  icon: string;
  name: string;
  discipline: string;
  color: string;
  desc: string;
  kps: string;
}

interface CourseCarousel3DProps {
  items: CarouselItem[];
  /** 自动轮播间隔（毫秒），0 关闭 */
  autoInterval?: number;
}

const CourseCarousel3D: React.FC<CourseCarousel3DProps> = ({
  items,
  autoInterval = 3800,
}) => {
  const [active, setActive] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const autoRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const pausedRef = useRef(false);

  const total = items.length;

  const rotateTo = (index: number) => {
    const el = containerRef.current;
    if (!el) return;
    // 环形旋转：整体 rotateY，让目标卡片正对前方
    const angle = (360 / total) * index;
    const cards = el.querySelectorAll<HTMLElement>("[data-carousel-card]");
    // 高亮目标卡片，其余变暗（层级感）
    gsap.to(cards, {
      opacity: (i: number) => (i === index ? 1 : 0.55),
      duration: 0.6,
    });
    gsap.to(el, {
      rotateY: -angle,
      duration: 1.1,
      ease: "power3.inOut",
      transformPerspective: 900,
    });
    setActive(((index % total) + total) % total);
  };

  useEffect(() => {
    // 初始布局：每张卡片分布在环形位置（环形半径 -280px，透视 900 更立体）
    const el = containerRef.current;
    if (!el) return;
    const cards = el.querySelectorAll<HTMLElement>("[data-carousel-card]");
    const step = 360 / total;
    gsap.set(cards, {
      rotateY: (i: number) => `${i * step}deg`,
      transformOrigin: "50% 50% -280px",
      z: -280,
      opacity: 0.6,
    });
    // 首张卡片高亮
    gsap.to(cards[0], { opacity: 1, duration: 0.4 });
    gsap.set(el, { transformPerspective: 900 });
  }, [total]);

  // 自动轮播
  useEffect(() => {
    if (autoInterval <= 0) return;
    autoRef.current = setInterval(() => {
      if (!pausedRef.current) rotateTo(active + 1);
    }, autoInterval);
    return () => {
      if (autoRef.current) clearInterval(autoRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoInterval, active]);

  return (
    <div
      className="flex flex-col items-center select-none"
      onMouseEnter={() => (pausedRef.current = true)}
      onMouseLeave={() => (pausedRef.current = false)}
    >
      {/* 3D 环形舞台 */}
      <div className="relative w-full max-w-4xl h-[380px] md:h-[420px] flex items-center justify-center [perspective:900px]">
        <div
          ref={containerRef}
          className="relative w-[280px] h-[300px] [transform-style:preserve-3d]"
        >
          {items.map((c, i) => {
            const isActive = i === active;
            return (
              <div
                key={c.name}
                data-carousel-card
                onClick={() => rotateTo(i)}
                className={`absolute inset-0 cursor-pointer transition-shadow duration-300 [backface-visibility:hidden] ${
                  isActive ? "shadow-2xl z-10" : "shadow-lg"
                }`}
              >
                <div className="h-full rounded-2xl bg-white border border-slate-100 shadow-card overflow-hidden">
                  <div className={`h-2 bg-gradient-to-r ${c.color}`} />
                  <div className="p-5 flex flex-col h-[calc(100%-8px)]">
                    <div className="text-4xl mb-3">{c.icon}</div>
                    <h3 className="text-xl font-semibold text-slate-900">
                      {c.name}
                    </h3>
                    <div
                      className={`text-xs font-medium mt-1 mb-2 ${
                        isActive ? "text-indigo-500" : "text-slate-400"
                      }`}
                    >
                      {c.discipline}
                    </div>
                    <p className="text-sm text-slate-500 leading-relaxed flex-1">
                      {c.desc}
                    </p>
                    <div className="mt-3 flex items-center gap-2">
                      <span
                        className={`px-2.5 py-1 rounded-full text-xs ${
                          isActive
                            ? "bg-indigo-50 text-indigo-600"
                            : "bg-slate-50 text-slate-500"
                        }`}
                      >
                        {c.kps}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 控制条 */}
      <div className="mt-6 flex items-center gap-6">
        <button
          onClick={() => rotateTo(active - 1)}
          className="w-10 h-10 rounded-full bg-white border border-slate-200 shadow-card flex items-center justify-center hover:bg-indigo-50 hover:border-indigo-200 transition-colors"
          aria-label="上一个"
        >
          <LeftOutlined className="text-slate-600" />
        </button>
        <div className="flex items-center gap-2">
          {items.map((c, i) => (
            <button
              key={c.name}
              onClick={() => rotateTo(i)}
              aria-label={`切换到 ${c.name}`}
              className={`h-2 rounded-full transition-all duration-300 ${
                i === active
                  ? "w-8 bg-primary"
                  : "w-2 bg-slate-300 hover:bg-slate-400"
              }`}
            />
          ))}
        </div>
        <button
          onClick={() => rotateTo(active + 1)}
          className="w-10 h-10 rounded-full bg-white border border-slate-200 shadow-card flex items-center justify-center hover:bg-indigo-50 hover:border-indigo-200 transition-colors"
          aria-label="下一个"
        >
          <RightOutlined className="text-slate-600" />
        </button>
      </div>
    </div>
  );
};

export default CourseCarousel3D;
