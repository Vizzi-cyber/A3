// @ts-nocheck
import React, { useEffect, useRef, useState, useCallback } from "react";
import { Spin, Empty, Modal } from "antd";
import { ExpandOutlined, CloseOutlined } from "@ant-design/icons";
import * as d3 from "d3";
import { kbApi } from "../../services/knowledgeBaseApi";

interface GraphData {
  nodes: { id: string; title: string }[];
  edges: { source: string; target: string }[];
}

interface KnowledgeGraphProps {
  onNoteClick?: (noteId: string) => void;
}

const KnowledgeGraph: React.FC<KnowledgeGraphProps> = ({ onNoteClick }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const simulationRef = useRef<d3.Simulation<any, any> | null>(null);

  const fetchGraph = useCallback(async () => {
    setLoading(true);
    try {
      const res = await kbApi.getGraph();
      if (res.data?.status === "success") {
        setGraphData(res.data.data);
      }
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchGraph();
  }, [fetchGraph]);

  const renderGraph = useCallback(() => {
    if (
      !graphData ||
      !svgRef.current ||
      !containerRef.current ||
      graphData.nodes.length === 0
    )
      return;

    // 停止之前的模拟
    if (simulationRef.current) {
      simulationRef.current.stop();
    }

    const svg = d3.select(svgRef.current);
    const container = containerRef.current;

    // 获取容器实际尺寸
    const rect = container.getBoundingClientRect();
    const width = rect.width || 300;
    const height = rect.height || 300;

    // 如果容器尺寸为0，跳过渲染
    if (width === 0 || height === 0) return;

    // 清空并设置 SVG
    svg.selectAll("*").remove();
    svg
      .attr("width", width)
      .attr("height", height)
      .attr("viewBox", `0 0 ${width} ${height}`);

    // 计算每个节点的链接数
    const linkCount = new Map<string, number>();
    graphData.nodes.forEach((n) => linkCount.set(n.id, 0));
    graphData.edges.forEach((e) => {
      const sourceId =
        typeof e.source === "string" ? e.source : (e.source as any).id;
      const targetId =
        typeof e.target === "string" ? e.target : (e.target as any).id;
      linkCount.set(sourceId, (linkCount.get(sourceId) || 0) + 1);
      linkCount.set(targetId, (linkCount.get(targetId) || 0) + 1);
    });

    const maxLinks = Math.max(1, ...Array.from(linkCount.values()));

    const nodes = graphData.nodes.map((n) => ({
      ...n,
      x: width / 2 + (Math.random() - 0.5) * width * 0.3,
      y: height / 2 + (Math.random() - 0.5) * height * 0.3,
      size: 5 + ((linkCount.get(n.id) || 1) / maxLinks) * 12,
    }));
    const edges = graphData.edges.map((e) => ({ ...e }));

    const simulation = d3
      .forceSimulation(nodes)
      .force(
        "link",
        d3
          .forceLink(edges)
          .id((d: any) => d.id)
          .distance(Math.min(150, width * 0.4)),
      )
      .force("charge", d3.forceManyBody().strength(-Math.min(400, width * 1.5)))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(35))
      .force("x", d3.forceX(width / 2).strength(0.1))
      .force("y", d3.forceY(height / 2).strength(0.1));

    simulationRef.current = simulation;

    const g = svg.append("g");

    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on("zoom", (event: any) => {
        g.attr("transform", event.transform);
      });
    svg.call(zoom);

    // 绘制连线
    const link = g
      .append("g")
      .selectAll("line")
      .data(edges)
      .join("line")
      .attr("stroke", "#94a3b8")
      .attr("stroke-width", 1.5)
      .attr("stroke-opacity", 0.6);

    // 绘制节点
    const node = g
      .append("g")
      .selectAll<SVGGElement, any>("g")
      .data(nodes)
      .join("g")
      .attr("cursor", "pointer")
      .call(
        d3
          .drag<SVGGElement, any>()
          .on("start", (event: any, d: any) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on("drag", (event: any, d: any) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on("end", (event: any, d: any) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          }),
      )
      .on("click", (_event: any, d: any) => {
        _event.stopPropagation();
        onNoteClick?.(d.id);
      })
      .on("mouseenter", function (_event: any, d: any) {
        const connected = new Set<string>();
        connected.add(d.id);
        edges.forEach((e: any) => {
          const s = typeof e.source === "string" ? e.source : e.source.id;
          const t = typeof e.target === "string" ? e.target : e.target.id;
          if (s === d.id) connected.add(t);
          if (t === d.id) connected.add(s);
        });

        node
          .selectAll("circle")
          .attr("opacity", (_d: any) => (connected.has(_d.id) ? 1 : 0.15))
          .attr("stroke-width", (_d: any) => (_d.id === d.id ? 3 : 1.5));
        node
          .selectAll("text")
          .attr("opacity", (_d: any) => (connected.has(_d.id) ? 1 : 0.15));
        link
          .attr("opacity", (_e: any) => {
            const s = typeof _e.source === "string" ? _e.source : _e.source.id;
            const t = typeof _e.target === "string" ? _e.target : _e.target.id;
            return s === d.id || t === d.id ? 1 : 0.05;
          })
          .attr("stroke-width", (_e: any) => {
            const s = typeof _e.source === "string" ? _e.source : _e.source.id;
            const t = typeof _e.target === "string" ? _e.target : _e.target.id;
            return s === d.id || t === d.id ? 2.5 : 1.5;
          });
      })
      .on("mouseleave", function () {
        node.selectAll("circle").attr("opacity", 1).attr("stroke-width", 1.5);
        node.selectAll("text").attr("opacity", 1);
        link.attr("opacity", 0.6).attr("stroke-width", 1.5);
      });

    // 节点圆形
    node
      .append("circle")
      .attr("r", (d: any) => d.size || 8)
      .attr("fill", "#6366f1")
      .attr("fill-opacity", 0.9)
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5);

    // 节点文字
    node
      .append("text")
      .text((d: any) => d.title)
      .attr("dx", (d: any) => (d.size || 8) + 6)
      .attr("dy", 4)
      .attr("font-size", 12)
      .attr("fill", "#1e293b")
      .attr("pointer-events", "none")
      .attr("font-weight", "500");

    // 更新位置
    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);

      node.attr("transform", (d: any) => `translate(${d.x},${d.y})`);
    });
  }, [graphData, onNoteClick]);

  // 监听容器大小变化
  useEffect(() => {
    if (!containerRef.current) return;

    const observer = new ResizeObserver(() => {
      renderGraph();
    });
    observer.observe(containerRef.current);

    return () => observer.disconnect();
  }, [renderGraph]);

  // 初始渲染
  useEffect(() => {
    if (graphData && graphData.nodes.length > 0) {
      const timer = setTimeout(renderGraph, 100);
      return () => clearTimeout(timer);
    }
  }, [graphData, renderGraph]);

  // 展开时重新渲染
  useEffect(() => {
    if (expanded) {
      const timer = setTimeout(renderGraph, 100);
      return () => clearTimeout(timer);
    }
  }, [expanded, renderGraph]);

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <Spin />
      </div>
    );
  }

  if (!graphData || graphData.nodes.length === 0) {
    return (
      <div className="h-full flex items-center justify-center">
        <Empty
          description="暂无图谱数据"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </div>
    );
  }

  const graphContent = (
    <div
      ref={containerRef}
      className="w-full h-full bg-white relative"
      style={{ minHeight: 200 }}
    >
      <svg
        ref={svgRef}
        className="w-full h-full"
        style={{ display: "block", width: "100%", height: "100%" }}
      ></svg>
      {/* 图例 */}
      <div className="absolute bottom-2 left-2 bg-white/90 backdrop-blur-sm rounded-lg px-3 py-2 text-xs text-slate-500 border border-slate-200 shadow-sm z-10">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-indigo-500"></span>
            笔记
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-6 h-px bg-slate-400"></span>
            WikiLink
          </span>
        </div>
        <div className="mt-1 text-slate-400">
          拖拽节点 · 滚轮缩放 · 点击跳转
        </div>
      </div>
    </div>
  );

  return (
    <>
      <div className="h-full flex flex-col">
        <div className="px-3 py-2 border-b border-slate-200 shrink-0 flex items-center justify-between">
          <div>
            <span className="text-sm font-medium text-slate-700">知识图谱</span>
            <span className="ml-2 text-xs text-slate-400">
              {graphData.nodes.length} 笔记 · {graphData.edges.length} 链接
            </span>
          </div>
          <button
            onClick={() => setExpanded(true)}
            className="p-1 rounded hover:bg-slate-100 text-slate-400 hover:text-indigo-600 transition-colors"
            title="展开图谱"
          >
            <ExpandOutlined />
          </button>
        </div>
        <div className="flex-1 min-h-0 overflow-hidden">{graphContent}</div>
      </div>

      {/* 全屏展开模态框 */}
      <Modal
        open={expanded}
        onCancel={() => setExpanded(false)}
        footer={null}
        width="90vw"
        style={{ top: 20 }}
        styles={{ body: { height: "calc(90vh - 55px)", padding: 0 } }}
        closeIcon={<CloseOutlined className="text-slate-500" />}
        destroyOnClose
      >
        <div className="h-full">{graphContent}</div>
      </Modal>
    </>
  );
};

export default KnowledgeGraph;
