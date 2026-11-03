import React, { useEffect, useRef } from "react";
import { Markmap } from "markmap-view";
import { Transformer } from "markmap-lib";

const transformer = new Transformer();

interface MindmapViewProps {
  content: string;
  style?: React.CSSProperties;
}

const MindmapView: React.FC<MindmapViewProps> = ({ content, style }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const mmRef = useRef<Markmap | null>(null);
  const stateRef = useRef({
    x: 0,
    y: 0,
    dragging: false,
    startX: 0,
    startY: 0,
  });

  useEffect(() => {
    if (!svgRef.current || !content.trim()) return;
    const svg = svgRef.current;
    while (svg.firstChild) svg.removeChild(svg.firstChild);

    const { root } = transformer.transform(content);
    mmRef.current = Markmap.create(svg, { duration: 300 } as any, root);

    // 等渲染完手动缩放居中
    const timer = setTimeout(() => {
      const g = svg.querySelector("g") as SVGGElement | null;
      if (!g) return;
      const bbox = g.getBBox?.();
      if (!bbox || !bbox.width) return;
      const w = svg.clientWidth || 600;
      const h = svg.clientHeight || 400;
      const scale = Math.min(
        w / (bbox.width + 60),
        h / (bbox.height + 60),
        2.5,
      );
      const tx = (w - bbox.width * scale) / 2 - bbox.x * scale;
      const ty = (h - bbox.height * scale) / 2 - bbox.y * scale;
      g.setAttribute("transform", `translate(${tx},${ty}) scale(${scale})`);
      stateRef.current = {
        x: tx,
        y: ty,
        dragging: false,
        startX: 0,
        startY: 0,
      };
    }, 200);

    return () => {
      clearTimeout(timer);
      mmRef.current?.destroy();
    };
  }, [content]);

  const onPointerDown = (e: React.PointerEvent) => {
    if (e.button !== 0) return;
    stateRef.current.dragging = true;
    stateRef.current.startX = e.clientX - (stateRef.current.x || 0);
    stateRef.current.startY = e.clientY - (stateRef.current.y || 0);
    svgRef.current?.setPointerCapture(e.pointerId);
  };

  const onPointerMove = (e: React.PointerEvent) => {
    if (!stateRef.current.dragging) return;
    const g = svgRef.current?.querySelector("g");
    if (!g) return;
    stateRef.current.x = e.clientX - stateRef.current.startX;
    stateRef.current.y = e.clientY - stateRef.current.startY;
    if (!isNaN(stateRef.current.x) && !isNaN(stateRef.current.y)) {
      g.setAttribute(
        "transform",
        `translate(${stateRef.current.x},${stateRef.current.y})`,
      );
    }
  };

  const onPointerUp = () => {
    stateRef.current.dragging = false;
  };

  if (!content.trim()) {
    return (
      <div className="flex items-center justify-center h-[300px] text-slate-400 text-sm">
        暂无思维导图数据
      </div>
    );
  }

  return (
    <svg
      ref={svgRef}
      style={{
        width: "100%",
        height: 420,
        cursor: "grab",
        userSelect: "none",
        ...style,
      }}
      className="block rounded-xl"
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
    />
  );
};

export default MindmapView;
