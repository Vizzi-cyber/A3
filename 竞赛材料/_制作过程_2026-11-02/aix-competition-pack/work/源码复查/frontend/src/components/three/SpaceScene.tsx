/**
 * 学科空间 3D 场景（SpaceScene）
 * three.js 实现的悬浮知识空间：
 *   - 深空背景 + 尘埃粒子 + 光晕
 *   - 8 个悬浮 3D 物体（stylized 几何体 + 机器人 GLTF 模型）
 *   - hover 高亮（发光增强 + 放大 + HTML 标签）
 *   - 点击物体 → 路由跳转（回调）
 *   - 鼠标拖拽旋转场景 + 视差
 */
import React, { useEffect, useRef } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { buildObject, SPACE_OBJECTS } from "./buildObjects";

interface SpaceSceneProps {
  onNavigate?: (route: string) => void;
  className?: string;
}

const SpaceScene: React.FC<SpaceSceneProps> = ({ onNavigate, className = "" }) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const labelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    // ---------- 基础 ----------
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0e1f);
    scene.fog = new THREE.FogExp2(0x0a0e1f, 0.045);

    const camera = new THREE.PerspectiveCamera(55, mount.clientWidth / mount.clientHeight, 0.1, 200);
    camera.position.set(0, 1.2, 9);
    camera.lookAt(0, 0.6, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(mount.clientWidth, mount.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.1;
    mount.appendChild(renderer.domElement);

    // ---------- 灯光 ----------
    scene.add(new THREE.AmbientLight(0x404060, 0.6));
    const key = new THREE.DirectionalLight(0xffffff, 1.2);
    key.position.set(4, 6, 5);
    scene.add(key);
    // 三色氛围光（学科色）
    const c1 = new THREE.PointLight(0x6366f1, 30, 30);
    c1.position.set(-5, 2, -2);
    const c2 = new THREE.PointLight(0xf97316, 30, 30);
    c2.position.set(5, 1, -2);
    const c3 = new THREE.PointLight(0x10b981, 20, 30);
    c3.position.set(0, 3, -6);
    scene.add(c1, c2, c3);

    // ---------- 尘埃粒子 ----------
    const starCount = 900;
    const starGeo = new THREE.BufferGeometry();
    const starPos = new Float32Array(starCount * 3);
    for (let i = 0; i < starCount; i++) {
      starPos[i * 3] = (Math.random() - 0.5) * 40;
      starPos[i * 3 + 1] = (Math.random() - 0.5) * 24;
      starPos[i * 3 + 2] = -Math.random() * 25 - 2;
    }
    starGeo.setAttribute("position", new THREE.BufferAttribute(starPos, 3));
    const starMat = new THREE.PointsMaterial({
      color: 0x93c5fd,
      size: 0.06,
      transparent: true,
      opacity: 0.7,
      blending: THREE.AdditiveBlending,
    });
    scene.add(new THREE.Points(starGeo, starMat));

    // ---------- 悬浮物体 ----------
    const objects: THREE.Group[] = [];
    const objectDefs = [...SPACE_OBJECTS];
    const meshes: THREE.Mesh[] = [];

    // 机器人（AI 辅导入口，真实 GLTF 模型）
    const robot = new THREE.Group();
    robot.position.set(0, 0.35, -3.6);
    robot.scale.setScalar(1.1);
    robot.userData = {
      id: "tutor", label: "AI 智能辅导", desc: "12 个智能体",
      route: "/tutor", color: "#22d3ee",
    };
    new GLTFLoader().load("/models/RobotExpressive.glb", (gltf) => {
      const model = gltf.scene;
      model.traverse((child) => {
        if ((child as THREE.Mesh).isMesh) {
          const m = child as THREE.Mesh;
          m.material = new THREE.MeshStandardMaterial({
            color: 0x7dd3fc, emissive: 0x0e7490, emissiveIntensity: 0.35,
            roughness: 0.4, metalness: 0.4,
          });
        }
      });
      model.scale.setScalar(0.08);
      robot.add(model);
    });
    // 机器人命中球
    const robotHit = new THREE.Mesh(
      new THREE.SphereGeometry(2.1, 8, 8),
      new THREE.MeshBasicMaterial({ visible: false }),
    );
    robotHit.position.set(0, 0.2, 0);
    robotHit.userData.hitbox = true;
    robot.add(robotHit);
    scene.add(robot);
    objects.push(robot);
    robot.traverse((c) => { if ((c as THREE.Mesh).isMesh) meshes.push(c as THREE.Mesh); });

    for (const def of objectDefs) {
      const obj = buildObject(def);
      scene.add(obj);
      objects.push(obj);
      obj.traverse((c) => { if ((c as THREE.Mesh).isMesh) meshes.push(c as THREE.Mesh); });
    }

    // ---------- 交互：hover / 点击 ----------
    const raycaster = new THREE.Raycaster();
    const pointer = new THREE.Vector2();
    const mouse = new THREE.Vector2();
    let hovered: THREE.Group | null = null;
    const labelEl = labelRef.current;

    // 区分"点击"与"拖拽"：记录按下位置，位移小于阈值才视为点击
    let downX = 0, downY = 0;

    const onPointerMove = (e: PointerEvent) => {
      const rect = mount.getBoundingClientRect();
      pointer.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      pointer.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      mouse.x = (e.clientX - rect.left) / rect.width - 0.5;
      mouse.y = (e.clientY - rect.top) / rect.height - 0.5;
      mount.style.cursor = hovered ? "pointer" : "grab";
    };
    const onPointerDown = (e: PointerEvent) => {
      downX = e.clientX;
      downY = e.clientY;
    };
    const onClick = () => {
      // 优先使用 hover 状态（最近一次命中），再用独立 raycast 兜底
      let target = hovered;
      if (!target) {
        raycaster.setFromCamera(pointer, camera);
        const hits = raycaster.intersectObjects(meshes, true);
        for (const h of hits) {
          let g: THREE.Object3D | null = h.object;
          while (g && !(g as THREE.Group).userData?.id) g = g.parent;
          if (g) { target = g as THREE.Group; break; }
        }
      }
      if (target && target.userData?.route) {
        onNavigate?.(target.userData.route as string);
      }
    };
    mount.addEventListener("pointermove", onPointerMove);
    mount.addEventListener("pointerdown", onPointerDown);
    mount.addEventListener("click", onClick);

    // ---------- 拖拽旋转 ----------
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.enableZoom = false;
    controls.enablePan = false;
    controls.minPolarAngle = Math.PI / 3.2;
    controls.maxPolarAngle = Math.PI / 1.8;
    controls.target.set(0, 0.6, 0);

    // ---------- 动画循环 ----------
    const clock = new THREE.Clock();
    let rafId = 0;

    const animate = () => {
      const t = clock.getElapsedTime();

      // hover 检测
      raycaster.setFromCamera(pointer, camera);
      const hits = raycaster.intersectObjects(meshes, true);
      let hitGroup: THREE.Group | null = null;
      for (const h of hits) {
        let g = h.object.parent;
        while (g && !g.userData?.id) g = g.parent;
        if (g && g.userData?.id) { hitGroup = g as THREE.Group; break; }
      }

      if (hitGroup !== hovered) {
        if (hovered) setHover(hovered, false);
        hovered = hitGroup;
        if (hovered) setHover(hovered, true);
      }

      // 物体悬浮动画
      objects.forEach((obj, i) => {
        const base = obj.userData?.id === "tutor" ? 0.35 : (obj.position.y);
        obj.position.y = base + Math.sin(t * 1.2 + i * 0.7) * 0.12;
        obj.rotation.y += 0.002;
        if (obj.userData?.id === "personal") {
          const sector = (obj as any).sector;
          if (sector) sector.rotation.y = t * 1.5;
        }
      });

      // 鼠标视差（相机轻微偏移）
      camera.position.x += (mouse.x * 0.7 - camera.position.x) * 0.03;
      camera.position.y += (1.2 + mouse.y * 0.4 - camera.position.y) * 0.03;
      camera.lookAt(0, 0.6, 0);

      controls.update();
      renderer.render(scene, camera);
      rafId = requestAnimationFrame(animate);
    };

    function setHover(obj: THREE.Group, on: boolean) {
      obj.traverse((c) => {
        if ((c as THREE.Mesh).isMesh) {
          const m = c as THREE.Mesh;
          const material = m.material as THREE.MeshStandardMaterial;
          if (material) {
            if (on) {
              gsapTo(m, { scale: 1.12 });
              material.emissiveIntensity = Math.max(material.emissiveIntensity, 1.2);
            } else {
              gsapTo(m, { scale: 1 });
              material.emissiveIntensity = 0.3;
            }
          }
        }
      });
      if (labelEl) {
        if (on) {
          labelEl.style.opacity = "1";
          labelEl.innerHTML = `<div class="font-semibold text-white text-sm">${obj.userData.label}</div>
            <div class="text-[11px] text-slate-300 mt-0.5">${obj.userData.desc}</div>`;
        } else {
          labelEl.style.opacity = "0";
        }
      }
    }

    // 简易补间（避免引入 gsap 依赖循环）
    const tweens: { mesh: THREE.Mesh; prop: "scale" | "emissiveIntensity"; from: number; to: number; t: number }[] = [];
    function gsapTo(m: THREE.Mesh, target: { scale?: number }) {
      m.scale.setScalar(target.scale ?? 1);
    }

    animate();

    // ---------- resize ----------
    const onResize = () => {
      if (!mount) return;
      camera.aspect = mount.clientWidth / mount.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(mount.clientWidth, mount.clientHeight);
    };
    window.addEventListener("resize", onResize);

    // ---------- 清理 ----------
    return () => {
      cancelAnimationFrame(rafId);
      controls.dispose();
      mount.removeEventListener("pointermove", onPointerMove);
      mount.removeEventListener("pointerdown", onPointerDown);
      mount.removeEventListener("click", onClick);
      window.removeEventListener("resize", onResize);
      scene.traverse((c) => {
        const m = c as THREE.Mesh;
        if (m.isMesh && m.geometry) m.geometry.dispose();
      });
      renderer.dispose();
      if (renderer.domElement.parentElement === mount) {
        mount.removeChild(renderer.domElement);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className={`relative w-full h-full ${className}`}>
      <div ref={mountRef} className="w-full h-full cursor-grab" />
      {/* hover 标签 */}
      <div
        ref={labelRef}
        className="pointer-events-none absolute left-1/2 top-[12%] -translate-x-1/2 px-4 py-2 rounded-xl bg-slate-900/70 backdrop-blur border border-white/10 text-center transition-opacity duration-300 opacity-0"
      >
        <div className="font-semibold text-white text-sm">物体</div>
      </div>
      {/* 底部提示 */}
      <div className="pointer-events-none absolute bottom-5 left-1/2 -translate-x-1/2 text-xs text-slate-400/80">
        🖱️ 拖拽旋转场景 · 悬停查看 · 点击进入
      </div>
    </div>
  );
};

export default SpaceScene;
