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

    if (!scrollTrigger) {
      play();
      return;
    }

    // 初始显示 0，滚动到视口才滚动
    import("gsap/ScrollTrigger").then(({ ScrollTrigger }) => {
      gsap.registerPlugin(ScrollTrigger);
      const st = ScrollTrigger.create({
        trigger: el,
        start: "top 92%",
        once: true,
        onEnter: play,
      });
      return () => st.kill();
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
