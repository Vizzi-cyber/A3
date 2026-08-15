/**
 * 3D 粒子网络背景（ParticleNetwork）
 * 数千粒子在空间中缓慢漂移，邻近粒子之间实时连线（类 AI 神经网络视觉）。
 * 算法：每帧计算粒子对距离（欧氏距离 < 阈值则连线），动态更新 LineSegments。
 * 替换原 Grid 网格地面——更高级、更有"数据流动"感。
 */
import React, { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

interface ParticleNetworkProps {
  count?: number;
  linkDistance?: number;
  particleColor?: string;
  linkColor?: string;
  radius?: number;
}

/** 伪 3D 噪声（sine 组合，连续有机，用于流场驱动） */
function pseudoNoise3(x: number, y: number, z: number): number {
  return (
    Math.sin(x * 1.7 + Math.sin(y * 1.3) + z * 0.9) +
    Math.sin(y * 1.4 + Math.sin(z * 1.2) + x * 0.8) +
    Math.sin(z * 1.6 + Math.sin(x * 1.1) + y * 1.0)
  );
}

const ParticleNetwork: React.FC<ParticleNetworkProps> = ({
  count = 300,
  linkDistance = 1.9,
  particleColor = "#818cf8",
  linkColor = "#6366f1",
  radius = 7,
}) => {
  const pointsRef = useRef<THREE.Points>(null);
  const linesRef = useRef<THREE.LineSegments>(null);

  // 粒子初始位置（球壳）
  const { positions, phases } = useMemo(() => {
    const pos = new Float32Array(count * 3);
    const ph = new Float32Array(count);
    for (let i = 0; i < count; i++) {
      const r = radius * Math.cbrt(Math.random());
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      pos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta) * 0.7;
      pos[i * 3 + 2] = r * Math.cos(phi);
      ph[i] = Math.random() * Math.PI * 2;
    }
    return { positions: pos, phases: ph };
  }, [count, radius]);

  // 连线缓冲（最多 count²/2 对，动态写入）
  const linePositions = useMemo(() => {
    const maxLinks = count * 24;
    return new Float32Array(maxLinks * 6);
  }, [count]);

  const linkCountRef = useRef(0);

  // 鼠标 3D 位置（z=0 平面投影，用于扰动）
  const mouse3D = useRef<THREE.Vector3>(new THREE.Vector3(99, 99, 99));
  const mouseActive = useRef(false);

  useFrame((state, delta) => {
    const points = pointsRef.current;
    const lines = linesRef.current;
    if (!points || !lines) return;

    const attr = points.geometry.attributes.position as THREE.BufferAttribute;
    const pos = attr.array as Float32Array;
    const t = state.clock.elapsedTime;
    const dt = Math.min(delta, 0.05);

    // ---- 流场运动：粒子沿 3D 伪噪声场的轨迹流动（有机曲线，非直线） ----
    const scale = 0.24;      // 噪声空间尺度
    const speed = 1.5;       // 流动速度
    for (let i = 0; i < count; i++) {
      const x = pos[i * 3], y = pos[i * 3 + 1], z = pos[i * 3 + 2];
      // 三个噪声维度 → 速度方向（轨迹随时间和位置连续变化）
      const n1 = pseudoNoise3(x * scale + t * 0.16, y * scale, z * scale + t * 0.1) + phases[i];
      const n2 = pseudoNoise3(x * scale, y * scale + t * 0.13, z * scale + t * 0.18);
      const n3 = pseudoNoise3(x * scale + t * 0.1, y * scale + t * 0.06, z * scale);
      const vx = Math.sin(n1 * Math.PI) * speed * dt;
      const vy = Math.cos(n2 * Math.PI) * speed * dt * 0.8;
      const vz = Math.sin(n3 * Math.PI) * speed * dt;
      pos[i * 3] += vx;
      pos[i * 3 + 1] += vy;
      pos[i * 3 + 2] += vz;

      // 边界软回弹（拉回球壳内）
      for (let d = 0; d < 3; d++) {
        const v = pos[i * 3 + d];
        if (Math.abs(v) > radius) {
          pos[i * 3 + d] = Math.sign(v) * radius * 0.96;
        }
      }

      // ---- 鼠标扰动：粒子被鼠标位置推开（交互轨迹） ----
      if (mouseActive.current) {
        const dx = x - mouse3D.current.x;
        const dy = y - mouse3D.current.y;
        const dz = z - mouse3D.current.z;
        const dist2 = dx * dx + dy * dy + dz * dz;
        const influence = 2.2;
        if (dist2 < influence * influence) {
          const dist = Math.sqrt(dist2) + 1e-4;
          const force = (1 - dist / influence) * 2.4 * dt;
          pos[i * 3] += (dx / dist) * force;
          pos[i * 3 + 1] += (dy / dist) * force;
          pos[i * 3 + 2] += (dz / dist) * force;
        }
      }
    }
    attr.needsUpdate = true;

    // 邻近连线（CPU 距离计算）
    const dist2 = linkDistance * linkDistance;
    let linkCount = 0;
    const lineArr = linePositions;
    // 步进采样降低开销
    const step = count > 200 ? 2 : 1;
    for (let i = 0; i < count; i += step) {
      for (let j = i + step; j < count; j += step) {
        const dx = pos[i * 3] - pos[j * 3];
        const dy = pos[i * 3 + 1] - pos[j * 3 + 1];
        const dz = pos[i * 3 + 2] - pos[j * 3 + 2];
        const d2 = dx * dx + dy * dy + dz * dz;
        if (d2 < dist2) {
          if (linkCount >= lineArr.length / 6) break;
          lineArr[linkCount * 6] = pos[i * 3];
          lineArr[linkCount * 6 + 1] = pos[i * 3 + 1];
          lineArr[linkCount * 6 + 2] = pos[i * 3 + 2];
          lineArr[linkCount * 6 + 3] = pos[j * 3];
          lineArr[linkCount * 6 + 4] = pos[j * 3 + 1];
          lineArr[linkCount * 6 + 5] = pos[j * 3 + 2];
          linkCount++;
        }
      }
    }
    linkCountRef.current = linkCount;
    (lines.geometry.attributes.position as THREE.BufferAttribute).needsUpdate = true;
    lines.geometry.setDrawRange(0, linkCount * 2);
  });

  // 鼠标 3D 投影（z=0 平面）
  const plane = useMemo(() => new THREE.Plane(new THREE.Vector3(0, 0, 1), 0), []);
  const raycaster = useMemo(() => new THREE.Raycaster(), []);

  const onPointerMove = (e: any) => {
    // R3F 事件：e.camera + 相对画布的 offset
    const w = e.nativeEvent.target?.clientWidth || 1;
    const h = e.nativeEvent.target?.clientHeight || 1;
    const ndc = new THREE.Vector2(
      ((e.nativeEvent.offsetX || 0) / w) * 2 - 1,
      -((e.nativeEvent.offsetY || 0) / h) * 2 + 1,
    );
    raycaster.setFromCamera(ndc, e.camera);
    const hit = new THREE.Vector3();
    if (raycaster.ray.intersectPlane(plane, hit)) {
      mouse3D.current.copy(hit);
      mouseActive.current = true;
    }
  };
  const onPointerLeave = () => { mouseActive.current = false; };

  return (
    <group onPointerMove={onPointerMove} onPointerLeave={onPointerLeave}>
      <points ref={pointsRef}>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" args={[positions, 3]} />
        </bufferGeometry>
        <pointsMaterial
          color={particleColor}
          size={0.05}
          transparent
          opacity={0.75}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </points>
      <lineSegments ref={linesRef}>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" args={[linePositions, 3]} />
        </bufferGeometry>
        <lineBasicMaterial color={linkColor} transparent opacity={0.45} depthWrite={false} />
      </lineSegments>
    </group>
  );
};

export default ParticleNetwork;
