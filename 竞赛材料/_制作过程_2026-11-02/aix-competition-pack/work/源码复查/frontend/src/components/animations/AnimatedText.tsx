/**
 * 逐字错峰入场标题（AnimatedText）
 * 进入视口时每个字符依次入场（上浮 + 3D 翻转 + 淡入）。
 * 纯 GSAP 实现，无新依赖。
 */
import React, { useEffect, useRef } from "react";
import gsap from "gsap";

interface AnimatedTextProps {
  text: string;
  className?: string;
  /** 入场延迟（秒） */
  delay?: number;
  /** 相邻字符入场间隔（秒） */
  stagger?: number;
  /** 是否滚动到视口才触发（默认进入即触发） */
  scrollTrigger?: boolean;
}

const AnimatedText: React.FC<AnimatedTextProps> = ({
  text,
  className = "",
  delay = 0,
  stagger = 0.045,
  scrollTrigger = false,
}) => {
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const chars = el.querySelectorAll<HTMLElement>(".anim-char");

    const tweens = gsap.fromTo(
      chars,
      { y: 34, autoAlpha: 0, rotateX: -60, transformOrigin: "50% 0%" },
      {
        y: 0,
        autoAlpha: 1,
        rotateX: 0,
        duration: 0.65,
        stagger,
        delay,
        ease: "power3.out",
      },
    );

    if (scrollTrigger) {
      import("gsap/ScrollTrigger").then(({ ScrollTrigger }) => {
        gsap.registerPlugin(ScrollTrigger);
        const st = ScrollTrigger.create({
          trigger: el,
          start: "top 88%",
          onEnter: () => {
            tweens.play();
            st.kill();
          },
        });
        // 初始隐藏，滚动到视口才播放
        gsap.set(chars, { y: 34, autoAlpha: 0, rotateX: -60 });
        tweens.pause();
      });
      return () => {
        tweens.kill();
      };
    }

    return () => {
      tweens.kill();
    };
  }, [text, delay, stagger, scrollTrigger]);

  return (
    <span
      ref={ref}
      className={className}
      style={{ perspective: 600, display: "inline-block" }}
      aria-label={text}
    >
      {text.split("").map((ch, i) => (
        <span
          key={`${i}-${ch}`}
          className="anim-char inline-block will-change-transform"
          style={{ whiteSpace: ch === " " ? "pre" : "normal" }}
        >
          {ch === " " ? "\u00A0" : ch}
        </span>
      ))}
    </span>
  );
};

export default AnimatedText;
