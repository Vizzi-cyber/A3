import React, { useEffect, useRef } from "react";
import { Markmap } from "markmap-view";
import { Transformer } from "markmap-lib";

const transformer = new Transformer();

interface MindmapViewProps {
  /** markmap 支持的缩进文本或 Markdown */
  content: string;
  style?: React.CSSProperties;
}

const MindmapView: React.FC<MindmapViewProps> = ({ content, style }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const mmRef = useRef<Markmap | null>(null);

  useEffect(() => {
    if (!svgRef.current || !content.trim()) return;

    // 解析为 markmap 数据
    const { root } = transformer.transform(content);

    // 如果已经有实例，销毁重建
    if (mmRef.current) {
      mmRef.current.destroy();
      mmRef.current = null;
    }

    // 渲染
    mmRef.current = Markmap.create(
      svgRef.current,
      {
        duration: 300,
      } as any,
      root,
    );

    return () => {
      if (mmRef.current) {
        mmRef.current.destroy();
        mmRef.current = null;
      }
    };
  }, [content]);

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
        ...style,
      }}
      className="block rounded-xl"
    />
  );
};

export default MindmapView;
