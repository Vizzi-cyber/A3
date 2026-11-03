import React, { useRef, useEffect, useState, useCallback } from "react";
import * as d3 from "d3";

interface MindmapNode {
  id: string;
  label: string;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
  index?: number;
}

interface MindmapEdge {
  source: string;
  target: string;
}

interface MindmapTreeNode {
  name: string;
  children?: MindmapTreeNode[];
}

interface MindmapData {
  nodes?: MindmapNode[];
  edges?: MindmapEdge[];
  root?: string;
  children?: MindmapTreeNode[];
}

interface MindmapViewerProps {
  data: MindmapData;
  width?: number;
  height?: number;
}

/** 将 {root, children} 树结构转换为 {nodes, edges} 图结构 */
function treeToGraph(data: MindmapData): {
  nodes: MindmapNode[];
  edges: MindmapEdge[];
} {
  const nodes: MindmapNode[] = [];
  const edges: MindmapEdge[] = [];
  let idCounter = 0;

  const addNode = (label: string): string => {
    const id = `n${idCounter++}`;
    nodes.push({ id, label });
    return id;
  };

  const walk = (name: string, parentId: string | null) => {
    const id = addNode(name);
    if (parentId) edges.push({ source: parentId, target: id });
    return id;
  };

  const rootId = walk(data.root || "root", null);
  const queue: {
    name: string;
    parentId: string;
    children?: MindmapTreeNode[];
  }[] = [];
  (data.children || []).forEach((c) => {
    queue.push({ name: c.name, parentId: rootId, children: c.children });
  });

  while (queue.length) {
    const cur = queue.shift()!;
    const id = walk(cur.name, cur.parentId);
    (cur.children || []).forEach((c) => {
      queue.push({ name: c.name, parentId: id, children: c.children });
    });
  }

  return { nodes, edges };
}

const COLORS = [
  "#6366f1",
  "#8b5cf6",
  "#a78bfa",
  "#c084fc",
  "#818cf8",
  "#93c5fd",
  "#67e8f9",
  "#34d399",
  "#fbbf24",
  "#fb923c",
  "#f87171",
  "#e879f9",
];

const MindmapViewer: React.FC<MindmapViewerProps> = ({
  data,
  width = 600,
  height = 420,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const simRef = useRef<d3.Simulation<any, any> | null>(null);
  const [dims, setDims] = useState({ w: width, h: height });

  useEffect(() => {
    if (!containerRef.current) return;
    const obs = new ResizeObserver((entries) => {
      const { width: w, height: h } = entries[0].contentRect;
      if (w > 0 && h > 0) setDims({ w, h });
    });
    obs.observe(containerRef.current);
    return () => obs.disconnect();
  }, []);

  const renderGraph = useCallback(() => {
    // Stop previous simulation
    if (simRef.current) {
      simRef.current.stop();
      simRef.current = null;
    }

    if (!svgRef.current) return;

    // 统一数据格式：支持 {nodes, edges} 和 {root, children} 两种格式
    const graphData =
      data?.nodes && data.nodes.length > 0
        ? { nodes: data.nodes, edges: data.edges || [] }
        : data?.root
          ? treeToGraph(data)
          : null;

    if (!graphData) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const { w, h } = dims;

    // Build adjacency for coloring
    const adj = new Map<string, Set<string>>();
    graphData.edges.forEach((e) => {
      if (!adj.has(e.source)) adj.set(e.source, new Set());
      if (!adj.has(e.target)) adj.set(e.target, new Set());
      adj.get(e.source)!.add(e.target);
      adj.get(e.target)!.add(e.source);
    });

    // Color by connected component (BFS)
    const nodeColor = new Map<string, string>();
    let colorIdx = 0;
    graphData.nodes.forEach((n) => {
      if (nodeColor.has(n.id)) return;
      const color = COLORS[colorIdx % COLORS.length];
      const queue = [n.id];
      while (queue.length) {
        const cur = queue.shift()!;
        if (nodeColor.has(cur)) continue;
        nodeColor.set(cur, color);
        adj.get(cur)?.forEach((nbr) => {
          if (!nodeColor.has(nbr)) queue.push(nbr);
        });
      }
      colorIdx++;
    });

    // Prepare simulation data
    const nodes: MindmapNode[] = graphData.nodes.map((n, i) => ({
      ...n,
      index: i,
    }));
    const nodeMap = new Map(nodes.map((n) => [n.id, n]));
    const links = graphData.edges
      .filter((e) => nodeMap.has(e.source) && nodeMap.has(e.target))
      .map((e) => ({
        source: nodeMap.get(e.source)!,
        target: nodeMap.get(e.target)!,
      }));

    // Force simulation
    const sim = d3
      .forceSimulation(nodes as any)
      .force(
        "link",
        d3
          .forceLink(links as any)
          .id((d: any) => d.id)
          .distance(90),
      )
      .force("charge", d3.forceManyBody().strength(-220))
      .force("center", d3.forceCenter(w / 2, h / 2))
      .force("collision", d3.forceCollide().radius(50));

    simRef.current = sim;

    // Defs for arrows
    const defs = svg.append("defs");
    defs
      .append("marker")
      .attr("id", "mm-arrow")
      .attr("viewBox", "0 0 10 10")
      .attr("refX", 10)
      .attr("refY", 5)
      .attr("markerWidth", 6)
      .attr("markerHeight", 6)
      .attr("orient", "auto")
      .append("path")
      .attr("d", "M0,0 L10,5 L0,10 Z")
      .attr("fill", "#94a3b8");

    // Draw edges
    const edgeG = svg.append("g");
    const edge = edgeG
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke", "#cbd5e1")
      .attr("stroke-width", 1.5)
      .attr("marker-end", "url(#mm-arrow)");

    // Draw nodes
    const nodeG = svg.append("g");
    const node = nodeG
      .selectAll("g")
      .data(nodes)
      .join("g")
      .attr("cursor", "grab")
      .call(
        d3
          .drag<any, any>()
          .on("start", (event: any, d: any) => {
            if (!event.active) sim.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
            d3.select(event.sourceEvent.target.closest("g")).attr(
              "cursor",
              "grabbing",
            );
          })
          .on("drag", (event: any, d: any) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on("end", (event: any, d: any) => {
            if (!event.active) sim.alphaTarget(0);
            d.fx = null;
            d.fy = null;
            d3.select(event.sourceEvent.target.closest("g")).attr(
              "cursor",
              "grab",
            );
          }),
      );

    node
      .append("rect")
      .attr("rx", 8)
      .attr("ry", 8)
      .attr("fill", (d) => nodeColor.get(d.id) || "#6366f1")
      .attr("fill-opacity", 0.12)
      .attr("stroke", (d) => nodeColor.get(d.id) || "#6366f1")
      .attr("stroke-width", 1.5)
      .attr("stroke-opacity", 0.5);

    node
      .append("text")
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "central")
      .attr("fill", "#334155")
      .attr("font-size", "12px")
      .attr("font-weight", 500)
      .attr("pointer-events", "none")
      .text((d) => d.label);

    // Size rects after text renders
    node.each(function () {
      const g = d3.select(this);
      const textEl = g.select<SVGTextElement>("text").node();
      if (!textEl) return;
      try {
        const bbox = textEl.getBBox();
        g.select("rect")
          .attr("x", bbox.x - 10)
          .attr("y", bbox.y - 4)
          .attr("width", bbox.width + 20)
          .attr("height", bbox.height + 8);
      } catch {
        // getBBox fails if SVG is hidden; fallback to estimated size
        const d = g.datum() as MindmapNode;
        const label = d?.label || "";
        const estW = label.length * 7.5 + 20;
        g.select("rect")
          .attr("x", -estW / 2)
          .attr("y", -12)
          .attr("width", estW)
          .attr("height", 24);
      }
    });

    // Tick
    sim.on("tick", () => {
      edge
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);

      node.attr("transform", (d: any) => `translate(${d.x},${d.y})`);
    });
  }, [data, dims]);

  useEffect(() => {
    renderGraph();
    return () => {
      if (simRef.current) {
        simRef.current.stop();
        simRef.current = null;
      }
    };
  }, [renderGraph]);

  if (!data?.nodes?.length && !data?.root) {
    return (
      <div className="flex items-center justify-center h-[300px] text-slate-400 text-sm">
        暂无思维导图数据
      </div>
    );
  }

  return (
    <div ref={containerRef} className="w-full h-full min-h-[360px]">
      <svg ref={svgRef} width={dims.w} height={dims.h} className="block" />
    </div>
  );
};

export default MindmapViewer;
