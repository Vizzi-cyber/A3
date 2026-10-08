/**
 * 数字滚动（CountUp）
 * 进入视口时数字从 0 滚动到目标值，支持小数位与千分位。
 */
import React, { useEffect, useRef, useState } from "react";
import gsap from "gsap";

interface CountUpProps {
  value: number;
  duration?: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  className?: string;
  /** 滚动到视口才触发（默认 true） */
  scrollTrigger?: boolean;
}

const CountUp: React.FC<CountUpProps> = ({
  value,
  duration = 1.6,
  decimals = 0,
  prefix = "",
  suffix = "",
  className = "",
  scrollTrigger = true,
}) => {
  const ref = useRef<HTMLSpanElement>(null);
  const [display, setDisplay] = useState(0);
  const playedRef = useRef(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    // StrictMode 下 effect 会执行两次（挂载→卸载→再挂载），useRef 不会随之重置。
    // 若不复位标志位，第二次执行时 play() 会被直接 return，数字永远停在 0。
    playedRef.current = false;

    const play = () => {
      if (playedRef.current) return;
      playedRef.current = true;
      const obj = { v: 0 };
      gsap.to(obj, {
        v: value,
        duration,
        ease: "power2.out",
        onUpdate: () => setDisplay(obj.v),
      });
    };

    // 关闭滚动触发，或元素已在视口内 → 立即播放
    //   首屏元素在 ScrollTrigger 建立前就已越过触发线，onEnter 不会触发，
    //   会导致数字停在 0（滚动一下才出现）。这里显式判断一次。
    const inViewport = () => {
      const r = el.getBoundingClientRect();
      return r.top < window.innerHeight * 0.95 && r.bottom > 0;
    };
    if (!scrollTrigger || inViewport()) {
      play();
      return;
    }

    // 初始显示 0，滚动到视口才滚动
    let killed = false;
    let killSt: (() => void) | undefined;
    import("gsap/ScrollTrigger").then(({ ScrollTrigger }) => {
      if (killed) return; // 组件已卸载，不再创建
      gsap.registerPlugin(ScrollTrigger);
      const st = ScrollTrigger.create({
        trigger: el,
        start: "top 95%",
        once: true,
        onEnter: play,
      });
      killSt = () => st.kill();
      // 异步加载期间元素可能已滚入视口
      if (inViewport()) play();
    });

    return () => {
      killed = true;
      killSt?.();
    };
  }, [value, duration, scrollTrigger]);

  const formatted = display.toLocaleString("zh-CN", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });

  return (
    <span ref={ref} className={className}>
      {prefix}
      {formatted}
      {suffix}
    </span>
  );
};

export default CountUp;
