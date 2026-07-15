import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Button, Collapse } from "antd";
import {
  RobotOutlined,
  CompassOutlined,
  MessageOutlined,
  TrophyOutlined,
  LineChartOutlined,
  FileTextOutlined,
  ArrowRightOutlined,
  MenuOutlined,
  CloseOutlined,
  CheckCircleOutlined,
  ApartmentOutlined,
  NodeIndexOutlined,
  SafetyCertificateOutlined,
  ThunderboltOutlined,
  CodeOutlined,
  BookOutlined,
  LockOutlined,
  EyeOutlined,
  DatabaseOutlined,
  BugOutlined,
  DownOutlined,
} from "@ant-design/icons";

gsap.registerPlugin(ScrollTrigger);

const navLinks = [
  { label: "功能", href: "#features" },
  { label: "产品", href: "#showcase" },
  { label: "流程", href: "#workflow" },
  { label: "FAQ", href: "#faq" },
];

const features = [
  {
    icon: <ApartmentOutlined className="text-xl" />,
    title: "多智能体协同",
    desc: "12个AI智能体协作——课程设计师、画像师、路径规划师、资源生成师、辅导助手等，覆盖学习全场景。",
    color: "bg-indigo-50 text-indigo-600",
  },
  {
    icon: <NodeIndexOutlined className="text-xl" />,
    title: "个性化路径规划",
    desc: "基于DAG知识图谱与学习画像，动态生成学习路径，实时调整策略，确保每一步精准高效。",
    color: "bg-sky-50 text-sky-600",
  },
  {
    icon: <MessageOutlined className="text-xl" />,
    title: "AI 苏格拉底式辅导",
    desc: "不是直接给答案，而是引导你思考。24小时在线答疑，支持图文输入与代码纠错。",
    color: "bg-emerald-50 text-emerald-600",
  },
  {
    icon: <TrophyOutlined className="text-xl" />,
    title: "游戏化学习激励",
    desc: "知识树成长、经验等级、成就徽章、六维排行榜、学习挑战任务，让学习充满成就感。",
    color: "bg-amber-50 text-amber-600",
  },
  {
    icon: <LineChartOutlined className="text-xl" />,
    title: "智能效果评估",
    desc: "多因子趋势分析，自动预测掌握度，生成干预策略。数据驱动，让进步肉眼可见。",
    color: "bg-rose-50 text-rose-600",
  },
  {
    icon: <FileTextOutlined className="text-xl" />,
    title: "自适应资源生成",
    desc: "讲解文档、练习题、思维导图、代码示例、PPT 一键生成，难度自适应，减少等待。",
    color: "bg-blue-50 text-blue-600",
  },
];

const steps = [
  {
    num: "01",
    title: "构建画像",
    desc: "系统通过多维评估，为你建立六维学习画像：知识基础、认知风格、薄弱环节、兴趣领域、学习习惯、情感状态。",
  },
  {
    num: "02",
    title: "规划路径",
    desc: "基于画像与知识图谱，AI 智能体协同规划最优学习路径，DAG 拓扑排序确保知识点循序渐进。",
  },
  {
    num: "03",
    title: "生成资源",
    desc: "根据你的画像自动调整资源难度与风格，生成文档、题目、代码示例，甚至完整的 PPT 课件。",
  },
  {
    num: "04",
    title: "智能辅导",
    desc: "学习过程中遇到疑难，AI 导师随时在线，苏格拉底式引导，帮助你真正理解而非记住答案。",
  },
];

const faqItems = [
  {
    key: "1",
    label: "系统支持哪些大模型？",
    children: (
      <p className="text-slate-500 text-sm leading-relaxed">
        目前支持讯飞星火、DeepSeek、OpenAI GPT-4 以及智谱 AI GLM-4
        等多种大模型，可在后台一键切换，无需修改代码。系统采用统一接口封装，方便后续扩展更多模型。
      </p>
    ),
  },
  {
    key: "2",
    label: "学生画像的六维具体指什么？",
    children: (
      <p className="text-slate-500 text-sm leading-relaxed">
        六维画像包括：知识基础（已掌握的知识点）、认知风格（视觉/逻辑/实践型）、薄弱环节（易错点与薄弱知识）、兴趣领域（学习偏好与目标）、学习习惯（时间分布与节奏）、情感状态（学习信心与压力）。系统通过对话分析与学习记录自动更新画像。
      </p>
    ),
  },
  {
    key: "3",
    label: "生成的学习资源可以下载或导出吗？",
    children: (
      <p className="text-slate-500 text-sm leading-relaxed">
        可以。讲解文档支持 Markdown 格式查看，思维导图支持导出图片，PPT
        课件支持直接下载 .pptx
        文件。代码示例支持在线运行，也可一键复制到本地编辑器。
      </p>
    ),
  },
  {
    key: "4",
    label: "多智能体之间如何协同工作？",
    children: (
      <p className="text-slate-500 text-sm leading-relaxed">
        系统基于 LangGraph
        构建多智能体工作流。课程设计师（Supervisor）负责任务分解与调度，画像师分析学习数据，路径规划师生成
        DAG
        学习路径，资源生成师根据画像匹配并生成内容，辅导助手提供实时答疑。各智能体通过消息队列通信，执行结果自动汇总。
      </p>
    ),
  },
  {
    key: "5",
    label: "如何保证内容安全与防止 AI 幻觉？",
    children: (
      <p className="text-slate-500 text-sm leading-relaxed">
        系统内置多重安全机制：输入/输出敏感词过滤、Prompt 安全约束、JSON
        结构校验、代码语法检查、引用溯源验证。同时通过内容库优先匹配减少纯 LLM
        生成，降低幻觉风险。关键教学内容均经过规则算法校验。
      </p>
    ),
  },
];

/* ===== Browser Mockup Component ===== */
const BrowserMockup: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className = "" }) => (
  <div
    className={`rounded-2xl bg-slate-100 border border-slate-200 shadow-float overflow-hidden ${className}`}
  >
    {/* Browser chrome */}
    <div className="h-9 bg-slate-50 border-b border-slate-200 flex items-center px-4 gap-2">
      <div className="flex gap-1.5">
        <div className="w-2.5 h-2.5 rounded-full bg-rose-400" />
        <div className="w-2.5 h-2.5 rounded-full bg-amber-400" />
        <div className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
      </div>
      <div className="flex-1 mx-4">
        <div className="h-5 bg-white rounded-md border border-slate-200 flex items-center px-2">
          <LockOutlined className="text-slate-300 text-[10px] mr-1.5" />
          <span className="text-[10px] text-slate-400">
            learnlab.system/dashboard
          </span>
        </div>
      </div>
    </div>
    <div className="bg-white">{children}</div>
  </div>
);

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  const heroRef = useRef<HTMLDivElement>(null);
  const featuresRef = useRef<HTMLDivElement>(null);
  const showcaseRef = useRef<HTMLDivElement>(null);
  const workflowRef = useRef<HTMLDivElement>(null);
  const ctaRef = useRef<HTMLDivElement>(null);
  const faqRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(
        ".hero-title",
        { y: 40, autoAlpha: 0 },
        { y: 0, autoAlpha: 1, duration: 1, ease: "power3.out", delay: 0.2 },
      );
      gsap.fromTo(
        ".hero-sub",
        { y: 30, autoAlpha: 0 },
        { y: 0, autoAlpha: 1, duration: 1, ease: "power3.out", delay: 0.5 },
      );
      gsap.fromTo(
        ".hero-cta",
        { y: 20, autoAlpha: 0 },
        { y: 0, autoAlpha: 1, duration: 0.8, ease: "power3.out", delay: 0.8 },
      );
      gsap.fromTo(
        ".hero-visual",
        { scale: 0.95, autoAlpha: 0 },
        {
          scale: 1,
          autoAlpha: 1,
          duration: 1.2,
          ease: "power3.out",
          delay: 0.6,
        },
      );

      gsap.fromTo(
        ".feature-card",
        { y: 40, autoAlpha: 0 },
        {
          y: 0,
          autoAlpha: 1,
          duration: 0.7,
          stagger: 0.1,
          ease: "power2.out",
          scrollTrigger: {
            trigger: featuresRef.current,
            start: "top 85%",
            toggleActions: "play none none none",
          },
        },
      );
      gsap.fromTo(
        ".showcase-item",
        { y: 50, autoAlpha: 0 },
        {
          y: 0,
          autoAlpha: 1,
          duration: 0.8,
          stagger: 0.2,
          ease: "power2.out",
          scrollTrigger: {
            trigger: showcaseRef.current,
            start: "top 85%",
            toggleActions: "play none none none",
          },
        },
      );
      gsap.fromTo(
        ".step-card",
        { y: 30, autoAlpha: 0 },
        {
          y: 0,
          autoAlpha: 1,
          duration: 0.8,
          stagger: 0.15,
          ease: "power2.out",
          scrollTrigger: {
            trigger: workflowRef.current,
            start: "top 85%",
            toggleActions: "play none none none",
          },
        },
      );
      gsap.fromTo(
        ".cta-content",
        { y: 30, autoAlpha: 0 },
        {
          y: 0,
          autoAlpha: 1,
          duration: 1,
          ease: "power2.out",
          scrollTrigger: {
            trigger: ctaRef.current,
            start: "top 85%",
            toggleActions: "play none none none",
          },
        },
      );
      gsap.fromTo(
        ".faq-content",
        { y: 30, autoAlpha: 0 },
        {
          y: 0,
          autoAlpha: 1,
          duration: 0.8,
          ease: "power2.out",
          scrollTrigger: {
            trigger: faqRef.current,
            start: "top 85%",
            toggleActions: "play none none none",
          },
        },
      );
    });
    return () => ctx.revert();
  }, []);

  const scrollTo = (href: string) => {
    const el = document.querySelector(href);
    if (el) el.scrollIntoView({ behavior: "smooth" });
    setMenuOpen(false);
  };

  return (
    <div className="relative bg-slate-50 text-slate-700 min-h-screen overflow-x-hidden">
      {/* ===== Navbar ===== */}
      <nav
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${scrolled ? "glass-strong border-b border-slate-200/50 shadow-soft" : "bg-transparent"}`}
      >
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div
            className="flex items-center gap-2 cursor-pointer"
            onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          >
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center shadow-glow">
              <RobotOutlined className="text-white text-sm" />
            </div>
            <span className="font-bold text-lg tracking-tight text-slate-900">
              LearnLab
            </span>
          </div>

          <div className="hidden lg:flex items-center gap-7">
            {navLinks.map((link) => (
              <button
                key={link.href}
                onClick={() => scrollTo(link.href)}
                className="text-sm text-slate-500 hover:text-primary transition-colors"
              >
                {link.label}
              </button>
            ))}
          </div>

          <div className="hidden md:flex items-center gap-3">
            <Button
              type="text"
              onClick={() => navigate("/login")}
              className="text-slate-600 hover:text-primary"
            >
              登录
            </Button>
            <Button
              type="primary"
              onClick={() => navigate("/login")}
              className="rounded-full bg-primary px-5 h-9 font-medium hover:bg-primary-700"
            >
              免费注册
            </Button>
          </div>

          <button
            className="md:hidden text-slate-700"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            {menuOpen ? <CloseOutlined /> : <MenuOutlined />}
          </button>
        </div>

        {menuOpen && (
          <div className="md:hidden bg-white/95 backdrop-blur-xl border-b border-slate-100 px-6 py-4 space-y-3 shadow-lg">
            {navLinks.map((link) => (
              <button
                key={link.href}
                onClick={() => scrollTo(link.href)}
                className="block w-full text-left text-slate-600 hover:text-primary py-2"
              >
                {link.label}
              </button>
            ))}
            <div className="pt-3 border-t border-slate-100 flex gap-3">
              <Button
                block
                onClick={() => navigate("/login")}
                className="rounded-full"
              >
                登录
              </Button>
              <Button
                block
                type="primary"
                onClick={() => navigate("/login")}
                className="rounded-full bg-primary"
              >
                注册
              </Button>
            </div>
          </div>
        )}
      </nav>

      {/* ===== Hero ===== */}
      <section
        ref={heroRef}
        className="relative pt-32 pb-20 md:pt-44 md:pb-32 px-6 overflow-hidden"
      >
        <div className="absolute inset-0 bg-mesh pointer-events-none" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-slate-50 pointer-events-none" />

        <div className="max-w-7xl mx-auto relative z-10">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="hero-title">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-100 text-xs text-primary font-medium mb-6">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                  第十五届中国软件杯 A3 赛题作品
                </div>
                <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold leading-[1.05] tracking-tighter text-slate-900">
                  让 AI 为你
                  <br />
                  <span className="text-primary">定制专属学习路径</span>
                </h1>
              </div>
              <p className="hero-sub mt-6 text-lg text-slate-500 max-w-lg leading-relaxed">
                基于大模型的多智能体协同系统，融合知识图谱、苏格拉底式辅导与游戏化激励，打造真正懂你的个性化学习平台。
              </p>
              <div className="hero-cta mt-8 flex flex-wrap gap-4">
                <Button
                  type="primary"
                  size="large"
                  onClick={() => navigate("/login")}
                  className="rounded-full bg-primary px-7 h-11 font-semibold hover:bg-primary-700 shadow-glow"
                >
                  <span className="flex items-center gap-2">
                    开始学习
                    <ArrowRightOutlined />
                  </span>
                </Button>
              </div>
              <div className="hero-cta mt-10 flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-slate-400">
                <div className="flex items-center gap-2">
                  <CheckCircleOutlined className="text-emerald-500" />
                  12个智能体协同
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircleOutlined className="text-emerald-500" />
                  DAG 路径规划
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircleOutlined className="text-emerald-500" />
                  实时效果评估
                </div>
              </div>
            </div>

            {/* Hero Visual - Dashboard Mockup */}
            <div className="hero-visual hidden lg:block">
              <BrowserMockup className="transform rotate-1 hover:rotate-0 transition-transform duration-500">
                <div className="p-4">
                  {/* Dashboard mock content */}
                  <div className="flex gap-3 mb-3">
                    <div className="w-1/3 h-20 rounded-xl bg-gradient-to-br from-indigo-50 to-white border border-indigo-100 p-3">
                      <div className="text-[10px] text-slate-400 mb-1">
                        本周学习时长
                      </div>
                      <div className="text-lg font-bold text-slate-800">
                        24.5
                        <span className="text-xs font-normal text-slate-400">
                          h
                        </span>
                      </div>
                      <div className="w-16 h-1 bg-indigo-100 rounded-full mt-2">
                        <div className="w-3/4 h-full bg-indigo-400 rounded-full" />
                      </div>
                    </div>
                    <div className="w-1/3 h-20 rounded-xl bg-gradient-to-br from-sky-50 to-white border border-sky-100 p-3">
                      <div className="text-[10px] text-slate-400 mb-1">
                        知识掌握度
                      </div>
                      <div className="text-lg font-bold text-slate-800">
                        87
                        <span className="text-xs font-normal text-slate-400">
                          %
                        </span>
                      </div>
                      <div className="w-16 h-1 bg-sky-100 rounded-full mt-2">
                        <div className="w-[87%] h-full bg-sky-400 rounded-full" />
                      </div>
                    </div>
                    <div className="w-1/3 h-20 rounded-xl bg-gradient-to-br from-emerald-50 to-white border border-emerald-100 p-3">
                      <div className="text-[10px] text-slate-400 mb-1">
                        连续打卡
                      </div>
                      <div className="text-lg font-bold text-slate-800">
                        12
                        <span className="text-xs font-normal text-slate-400">
                          天
                        </span>
                      </div>
                      <div className="flex gap-0.5 mt-2">
                        {Array.from({ length: 7 }).map((_, i) => (
                          <div
                            key={i}
                            className={`w-2 h-2 rounded-sm ${i < 5 ? "bg-emerald-400" : "bg-emerald-100"}`}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <div className="w-1/2 h-28 rounded-xl bg-slate-50 border border-slate-100 p-3">
                      <div className="text-[10px] text-slate-400 mb-2">
                        六维学习画像
                      </div>
                      <div className="flex items-center justify-center h-16">
                        <svg viewBox="0 0 100 80" className="w-20 h-16">
                          <polygon
                            points="50,5 85,25 75,65 25,65 15,25"
                            fill="none"
                            stroke="#e2e8f0"
                            strokeWidth="1"
                          />
                          <polygon
                            points="50,5 85,25 75,65 25,65 15,25"
                            fill="rgba(99,102,241,0.1)"
                            stroke="#6366f1"
                            strokeWidth="1.5"
                          />
                          <circle cx="50" cy="5" r="2" fill="#6366f1" />
                          <circle cx="85" cy="25" r="2" fill="#6366f1" />
                          <circle cx="75" cy="65" r="2" fill="#6366f1" />
                          <circle cx="25" cy="65" r="2" fill="#6366f1" />
                          <circle cx="15" cy="25" r="2" fill="#6366f1" />
                        </svg>
                      </div>
                    </div>
                    <div className="w-1/2 h-28 rounded-xl bg-slate-50 border border-slate-100 p-3">
                      <div className="text-[10px] text-slate-400 mb-2">
                        今日任务
                      </div>
                      <div className="space-y-1.5">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full bg-primary/10 flex items-center justify-center">
                            <CheckCircleOutlined className="text-[6px] text-primary" />
                          </div>
                          <div className="h-1.5 w-20 bg-slate-200 rounded-full" />
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full bg-sky-100 flex items-center justify-center">
                            <div className="w-1.5 h-1.5 rounded-full bg-sky-400" />
                          </div>
                          <div className="h-1.5 w-16 bg-slate-200 rounded-full" />
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full bg-slate-100" />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </BrowserMockup>

              {/* Floating cards */}
              <div className="absolute -top-4 -right-4 px-3 py-2 rounded-xl bg-white border border-slate-100 shadow-card flex items-center gap-2 animate-float">
                <div className="w-7 h-7 rounded-lg bg-indigo-50 flex items-center justify-center text-primary text-xs">
                  <RobotOutlined />
                </div>
                <div>
                  <div className="text-[10px] text-slate-400">AI 辅导</div>
                  <div className="text-xs font-semibold text-slate-700">
                    新消息 3
                  </div>
                </div>
              </div>
              <div
                className="absolute -bottom-4 -left-4 px-3 py-2 rounded-xl bg-white border border-slate-100 shadow-card flex items-center gap-2 animate-float"
                style={{ animationDelay: "1s" }}
              >
                <div className="w-7 h-7 rounded-lg bg-amber-50 flex items-center justify-center text-warning text-xs">
                  <TrophyOutlined />
                </div>
                <div>
                  <div className="text-[10px] text-slate-400">获得成就</div>
                  <div className="text-xs font-semibold text-slate-700">
                    连续学习 7 天
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== Trusted By / Models ===== */}
      <section className="py-10 border-y border-slate-100 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <p className="text-center text-xs text-slate-400 mb-6 tracking-wider uppercase">
            兼容主流大模型，一键切换
          </p>
          <div className="flex flex-wrap justify-center items-center gap-8 md:gap-14 opacity-60">
            {["讯飞星火", "DeepSeek", "OpenAI", "智谱 AI", "火山引擎"].map(
              (name) => (
                <div
                  key={name}
                  className="flex items-center gap-2 text-slate-500 font-semibold text-sm"
                >
                  <ThunderboltOutlined className="text-primary" />
                  {name}
                </div>
              ),
            )}
          </div>
        </div>
      </section>

      {/* ===== Features Bento Grid ===== */}
      <section
        id="features"
        ref={featuresRef}
        className="py-24 px-6 relative noise-overlay"
      >
        <div className="max-w-7xl mx-auto relative z-10">
          <div className="text-center mb-16">
            <div className="inline-block px-3 py-1 rounded-full bg-indigo-50 border border-indigo-100 text-primary text-xs font-medium mb-4">
              核心能力
            </div>
            <h2 className="text-3xl md:text-5xl font-bold text-slate-900 tracking-tight">
              12个智能体，全链路覆盖
            </h2>
            <p className="mt-4 text-slate-500 max-w-2xl mx-auto text-lg">
              从画像构建到路径规划，从资源生成到智能辅导，从错误诊断到项目协作，每个环节都有专属
              AI 智能体为你服务
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
            {features.map((f, i) => {
              const spanClass = [0, 3, 4].includes(i)
                ? "md:col-span-2 lg:col-span-2"
                : "md:col-span-1 lg:col-span-1";
              return (
                <div
                  key={i}
                  className={`feature-card tilt-card-wrap group relative ${spanClass} p-6 rounded-2xl bg-white border border-slate-100 shadow-card hover:shadow-card-hover transition-all duration-300 hover:-translate-y-1 overflow-hidden`}
                  onMouseMove={(e) => {
                    const card = e.currentTarget.querySelector(
                      ".tilt-card",
                    ) as HTMLElement;
                    if (!card) return;
                    const rect = e.currentTarget.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    const cx = rect.width / 2;
                    const cy = rect.height / 2;
                    const rotateX = ((y - cy) / cy) * -4;
                    const rotateY = ((x - cx) / cx) * 4;
                    card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
                  }}
                  onMouseLeave={(e) => {
                    const card = e.currentTarget.querySelector(
                      ".tilt-card",
                    ) as HTMLElement;
                    if (card)
                      card.style.transform =
                        "perspective(1000px) rotateX(0deg) rotateY(0deg)";
                  }}
                >
                  <div className="tilt-card transition-transform duration-150 ease-out">
                    <div className="tilt-card-content">
                      <div
                        className={`w-12 h-12 rounded-xl ${f.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}
                      >
                        {f.icon}
                      </div>
                      <h3 className="text-lg font-semibold text-slate-900 mb-2">
                        {f.title}
                      </h3>
                      <p className="text-sm text-slate-500 leading-relaxed">
                        {f.desc}
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ===== Product Showcase ===== */}
      <section
        id="showcase"
        ref={showcaseRef}
        className="py-24 px-6 bg-white border-y border-slate-100"
      >
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <div className="inline-block px-3 py-1 rounded-full bg-sky-50 border border-sky-100 text-secondary text-xs font-medium mb-4">
              产品演示
            </div>
            <h2 className="text-3xl md:text-5xl font-bold text-slate-900 tracking-tight">
              功能齐全，界面现代
            </h2>
            <p className="mt-4 text-slate-500 max-w-2xl mx-auto">
              从仪表盘到知识树，从智能辅导到学习挑战，为你提供沉浸式的学习体验
            </p>
          </div>

          {/* Main showcase - Dashboard */}
          <div className="showcase-item mb-8">
            <BrowserMockup className="max-w-5xl mx-auto">
              <div className="p-5">
                {/* Top bar */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded bg-primary flex items-center justify-center text-white text-[10px]">
                      <RobotOutlined />
                    </div>
                    <span className="text-xs font-semibold text-slate-700">
                      Dashboard
                    </span>
                  </div>
                  <div className="flex gap-2">
                    <div className="w-16 h-4 rounded-full bg-slate-100" />
                    <div className="w-4 h-4 rounded-full bg-slate-100" />
                  </div>
                </div>
                {/* Stats row */}
                <div className="grid grid-cols-4 gap-3 mb-4">
                  {["学习时长", "掌握度", "连续打卡", "生成资源"].map(
                    (label, i) => (
                      <div
                        key={i}
                        className="rounded-xl bg-slate-50 border border-slate-100 p-3"
                      >
                        <div className="text-[9px] text-slate-400 mb-1">
                          {label}
                        </div>
                        <div className="h-2 w-12 bg-slate-200 rounded-full mb-2" />
                        <div className="h-1.5 w-8 bg-slate-100 rounded-full" />
                      </div>
                    ),
                  )}
                </div>
                {/* Chart area */}
                <div className="flex gap-3">
                  <div className="w-2/3 rounded-xl bg-slate-50 border border-slate-100 p-3 h-32">
                    <div className="text-[9px] text-slate-400 mb-2">
                      学习趋势
                    </div>
                    <svg viewBox="0 0 200 60" className="w-full h-16">
                      <defs>
                        <linearGradient
                          id="chartGrad"
                          x1="0"
                          y1="0"
                          x2="0"
                          y2="1"
                        >
                          <stop
                            offset="0%"
                            stopColor="#6366f1"
                            stopOpacity="0.2"
                          />
                          <stop
                            offset="100%"
                            stopColor="#6366f1"
                            stopOpacity="0"
                          />
                        </linearGradient>
                      </defs>
                      <path
                        d="M0,45 Q30,35 50,40 T100,25 T150,30 T200,15"
                        fill="none"
                        stroke="#6366f1"
                        strokeWidth="1.5"
                      />
                      <path
                        d="M0,45 Q30,35 50,40 T100,25 T150,30 T200,15 V60 H0 Z"
                        fill="url(#chartGrad)"
                      />
                    </svg>
                  </div>
                  <div className="w-1/3 rounded-xl bg-slate-50 border border-slate-100 p-3 h-32">
                    <div className="text-[9px] text-slate-400 mb-2">
                      Agent 状态
                    </div>
                    <div className="space-y-2">
                      {["课程设计师", "画像师", "路径规划", "资源生成"].map(
                        (a, i) => (
                          <div key={i} className="flex items-center gap-2">
                            <div
                              className={`w-1.5 h-1.5 rounded-full ${i < 3 ? "bg-emerald-400" : "bg-slate-300"}`}
                            />
                            <div className="h-1.5 w-14 bg-slate-200 rounded-full" />
                          </div>
                        ),
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </BrowserMockup>
          </div>

          {/* Secondary showcases */}
          <div className="grid md:grid-cols-3 gap-6">
            {/* Knowledge Tree */}
            <div className="showcase-item">
              <BrowserMockup>
                <div className="p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <BookOutlined className="text-primary text-xs" />
                    <span className="text-xs font-semibold text-slate-700">
                      知识树
                    </span>
                  </div>
                  <div className="flex flex-col items-center gap-2">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-500 flex items-center justify-center text-white text-xs shadow-glow">
                      根
                    </div>
                    <div className="w-px h-3 bg-slate-200" />
                    <div className="flex gap-4">
                      <div className="flex flex-col items-center gap-1">
                        <div className="w-6 h-6 rounded-full bg-emerald-400 text-white text-[8px] flex items-center justify-center">
                          1
                        </div>
                        <div className="h-2 w-px bg-slate-200" />
                        <div className="w-5 h-5 rounded-full bg-emerald-300 text-white text-[7px] flex items-center justify-center">
                          1a
                        </div>
                      </div>
                      <div className="flex flex-col items-center gap-1">
                        <div className="w-6 h-6 rounded-full bg-emerald-400 text-white text-[8px] flex items-center justify-center">
                          2
                        </div>
                        <div className="h-2 w-px bg-slate-200" />
                        <div className="w-5 h-5 rounded-full bg-slate-200 text-slate-400 text-[7px] flex items-center justify-center">
                          2a
                        </div>
                      </div>
                      <div className="flex flex-col items-center gap-1">
                        <div className="w-6 h-6 rounded-full bg-emerald-400 text-white text-[8px] flex items-center justify-center">
                          3
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </BrowserMockup>
            </div>

            {/* AI Tutor */}
            <div className="showcase-item">
              <BrowserMockup>
                <div className="p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <MessageOutlined className="text-secondary text-xs" />
                    <span className="text-xs font-semibold text-slate-700">
                      AI 辅导
                    </span>
                  </div>
                  <div className="space-y-2">
                    <div className="flex gap-2">
                      <div className="w-5 h-5 rounded-full bg-slate-200 shrink-0" />
                      <div className="bg-slate-50 rounded-lg rounded-tl-none p-2 text-[9px] text-slate-600 leading-tight">
                        指针存储的是内存地址，你可以把它想象成门牌号...
                      </div>
                    </div>
                    <div className="flex gap-2 justify-end">
                      <div className="bg-primary text-white rounded-lg rounded-tr-none p-2 text-[9px] leading-tight">
                        那结构体指针呢？
                      </div>
                      <div className="w-5 h-5 rounded-full bg-indigo-100 shrink-0 flex items-center justify-center text-primary text-[8px]">
                        我
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <div className="w-5 h-5 rounded-full bg-slate-200 shrink-0" />
                      <div className="bg-slate-50 rounded-lg rounded-tl-none p-2 text-[9px] text-slate-600 leading-tight">
                        结构体指针就是指向一整栋房子的门牌号...
                      </div>
                    </div>
                  </div>
                </div>
              </BrowserMockup>
            </div>

            {/* Learning Path */}
            <div className="showcase-item">
              <BrowserMockup>
                <div className="p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <CompassOutlined className="text-warning text-xs" />
                    <span className="text-xs font-semibold text-slate-700">
                      学习路径
                    </span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-6 h-6 rounded-full bg-emerald-400 text-white text-[8px] flex items-center justify-center">
                      1
                    </div>
                    <div className="flex-1 h-px bg-emerald-200" />
                    <div className="w-6 h-6 rounded-full bg-emerald-400 text-white text-[8px] flex items-center justify-center">
                      2
                    </div>
                    <div className="flex-1 h-px bg-sky-200" />
                    <div className="w-6 h-6 rounded-full bg-sky-400 text-white text-[8px] flex items-center justify-center">
                      3
                    </div>
                    <div className="flex-1 h-px bg-slate-200" />
                    <div className="w-6 h-6 rounded-full bg-slate-200 text-slate-400 text-[8px] flex items-center justify-center">
                      4
                    </div>
                  </div>
                  <div className="mt-3 rounded-lg bg-slate-50 border border-slate-100 p-2">
                    <div className="text-[9px] text-slate-400 mb-1">
                      当前节点
                    </div>
                    <div className="text-xs font-medium text-slate-700">
                      指针与数组
                    </div>
                    <div className="mt-1 h-1 w-full bg-slate-200 rounded-full">
                      <div className="h-full w-2/3 bg-sky-400 rounded-full" />
                    </div>
                  </div>
                </div>
              </BrowserMockup>
            </div>
          </div>
        </div>
      </section>

      {/* ===== Security & Tech ===== */}
      <section className="py-20 px-6 bg-slate-50">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-block px-3 py-1 rounded-full bg-emerald-50 border border-emerald-100 text-emerald-600 text-xs font-medium mb-4">
                安全与质量
              </div>
              <h2 className="text-3xl md:text-5xl font-bold text-slate-900 mb-4 tracking-tight">
                多层防护，让 AI 输出更可靠
              </h2>
              <p className="text-slate-500 mb-8 leading-relaxed">
                教学场景对内容准确性要求极高。系统内置多重安全机制，从输入过滤到输出校验，全方位降低幻觉风险。
              </p>
              <div className="grid sm:grid-cols-2 gap-4">
                {[
                  {
                    icon: <LockOutlined />,
                    title: "敏感词过滤",
                    desc: "输入输出双向检测",
                  },
                  {
                    icon: <SafetyCertificateOutlined />,
                    title: "Prompt 加固",
                    desc: "自动追加安全约束",
                  },
                  {
                    icon: <CodeOutlined />,
                    title: "代码语法校验",
                    desc: "Python AST 静态检查",
                  },
                  {
                    icon: <EyeOutlined />,
                    title: "引用溯源",
                    desc: "知识点来源可追溯",
                  },
                  {
                    icon: <DatabaseOutlined />,
                    title: "内容库优先",
                    desc: "减少纯 LLM 生成",
                  },
                  {
                    icon: <BugOutlined />,
                    title: "JSON 结构校验",
                    desc: "严格 schema 验证",
                  },
                ].map((item, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-3 p-3 rounded-xl bg-white border border-slate-100 shadow-card"
                  >
                    <div className="w-8 h-8 rounded-lg bg-indigo-50 text-primary flex items-center justify-center text-sm shrink-0">
                      {item.icon}
                    </div>
                    <div>
                      <div className="text-sm font-medium text-slate-800">
                        {item.title}
                      </div>
                      <div className="text-xs text-slate-400">{item.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-tr from-indigo-100/50 to-sky-100/50 rounded-3xl blur-2xl" />
              <div className="relative bg-white rounded-3xl shadow-float border border-slate-100 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="text-sm font-semibold text-slate-800">
                    安全防护链路
                  </div>
                  <div className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600 text-[10px] font-medium">
                    运行中
                  </div>
                </div>
                <div className="space-y-3">
                  {[
                    {
                      step: "用户输入",
                      status: "已通过",
                      color: "bg-emerald-400",
                    },
                    {
                      step: "敏感词检测",
                      status: "已通过",
                      color: "bg-emerald-400",
                    },
                    {
                      step: "Prompt 安全加固",
                      status: "已通过",
                      color: "bg-emerald-400",
                    },
                    { step: "LLM 生成", status: "已完成", color: "bg-sky-400" },
                    {
                      step: "JSON / 代码校验",
                      status: "已通过",
                      color: "bg-emerald-400",
                    },
                    {
                      step: "引用溯源检查",
                      status: "已通过",
                      color: "bg-emerald-400",
                    },
                    {
                      step: "输出过滤",
                      status: "已通过",
                      color: "bg-emerald-400",
                    },
                  ].map((s, i) => (
                    <div key={i} className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full ${s.color}`} />
                      <div className="flex-1 text-xs text-slate-600">
                        {s.step}
                      </div>
                      <div className="text-[10px] text-slate-400">
                        {s.status}
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                  <div className="text-[10px] text-slate-400">平均响应时间</div>
                  <div className="text-xs font-semibold text-slate-700">
                    1.2s
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== Workflow ===== */}
      <section
        id="workflow"
        ref={workflowRef}
        className="py-24 px-6 bg-slate-50 relative"
      >
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <div className="inline-block px-3 py-1 rounded-full bg-sky-50 border border-sky-100 text-secondary text-xs font-medium mb-4">
              工作流程
            </div>
            <h2 className="text-3xl md:text-5xl font-bold text-slate-900 tracking-tight">
              四步开启智能学习
            </h2>
            <p className="mt-4 text-slate-500 max-w-2xl mx-auto">
              无需复杂配置，系统智能体自动协同，为你打造闭环学习体验
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 relative">
            <div className="hidden lg:block absolute top-12 left-[12.5%] right-[12.5%] h-0.5 bg-gradient-to-r from-indigo-200 via-sky-200 to-amber-200" />
            {steps.map((step, i) => (
              <div key={i} className="step-card relative text-center">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white font-bold text-sm mx-auto mb-4 relative z-10 ring-4 ring-slate-50">
                  {step.num}
                </div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2">
                  {step.title}
                </h3>
                <p className="text-sm text-slate-500 leading-relaxed">
                  {step.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
        {/* Wave divider to Testimonials */}
        <div className="wave-divider wave-divider-bottom">
          <svg
            data-name="Layer 1"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 1200 120"
            preserveAspectRatio="none"
          >
            <path
              d="M985.66,92.83C906.67,72,823.78,31,743.84,14.19c-82.26-17.34-168.06-16.33-250.45.39-57.84,11.73-114,31.07-172,41.86A600.21,600.21,0,0,1,0,27.35V120H1200V95.8C1132.19,118.92,1055.71,111.31,985.66,92.83Z"
              fill="#ffffff"
            ></path>
          </svg>
        </div>
      </section>

      {/* ===== FAQ ===== */}
      <section
        id="faq"
        ref={faqRef}
        className="py-24 px-6 bg-slate-50 relative noise-overlay"
      >
        <div className="max-w-3xl mx-auto relative z-10">
          <div className="text-center mb-12">
            <div className="inline-block px-3 py-1 rounded-full bg-blue-50 border border-blue-100 text-blue-600 text-xs font-medium mb-4">
              常见问题
            </div>
            <h2 className="text-3xl md:text-5xl font-bold text-slate-900 tracking-tight">
              有疑问？我们来解答
            </h2>
          </div>
          <div className="faq-content">
            <Collapse
              expandIcon={({ isActive }) => (
                <DownOutlined
                  className={`text-xs text-slate-400 transition-transform ${isActive ? "rotate-180" : ""}`}
                />
              )}
              expandIconPosition="end"
              className="bg-transparent border-0"
              items={faqItems.map((item) => ({
                key: item.key,
                label: (
                  <span className="text-sm font-medium text-slate-800">
                    {item.label}
                  </span>
                ),
                children: item.children,
                className:
                  "mb-3 rounded-xl bg-white border border-slate-100 shadow-card !border-solid",
              }))}
            />
          </div>
        </div>
        {/* Wave divider to CTA */}
        <div className="wave-divider wave-divider-bottom">
          <svg
            data-name="Layer 1"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 1200 120"
            preserveAspectRatio="none"
          >
            <path
              d="M985.66,92.83C906.67,72,823.78,31,743.84,14.19c-82.26-17.34-168.06-16.33-250.45.39-57.84,11.73-114,31.07-172,41.86A600.21,600.21,0,0,1,0,27.35V120H1200V95.8C1132.19,118.92,1055.71,111.31,985.66,92.83Z"
              fill="#ffffff"
            ></path>
          </svg>
        </div>
      </section>

      {/* ===== CTA ===== */}
      <section
        ref={ctaRef}
        className="py-24 px-6 bg-white noise-overlay relative"
      >
        <div className="max-w-4xl mx-auto relative z-10">
          <div className="cta-content relative p-10 md:p-20 rounded-3xl bg-gradient-to-br from-sky-50 to-indigo-50 text-center border border-sky-100 shadow-float">
            <div className="relative z-10">
              <h2 className="text-4xl md:text-6xl font-bold text-slate-900 mb-6 tracking-tight">
                准备好开启你的
                <br className="hidden sm:block" />
                AI 学习之旅了吗？
              </h2>
              <Button
                size="large"
                onClick={() => navigate("/login")}
                className="rounded-full bg-primary text-white hover:bg-primary/90 px-10 h-12 font-semibold border-0 hover:-translate-y-0.5 transition-all duration-300"
              >
                <span className="flex items-center gap-2 text-white">
                  免费开始使用
                  <ArrowRightOutlined />
                </span>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* ===== Footer ===== */}
      <footer className="border-t border-slate-100 py-12 px-6 bg-slate-50">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-10">
            <div className="md:col-span-1">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-7 h-7 rounded-md bg-primary flex items-center justify-center">
                  <RobotOutlined className="text-white text-xs" />
                </div>
                <span className="font-semibold text-slate-900">LearnLab</span>
              </div>
              <p className="text-xs text-slate-500 leading-relaxed">
                基于大模型的个性化资源生成与学习多智能体系统，第十五届中国软件杯大赛
                A3 赛题作品。
              </p>
            </div>
            <div>
              <div className="text-sm font-semibold text-slate-800 mb-3">
                产品功能
              </div>
              <div className="space-y-2 text-xs text-slate-500">
                <div>智能画像</div>
                <div>路径规划</div>
                <div>资源生成</div>
                <div>AI 辅导</div>
              </div>
            </div>
            <div>
              <div className="text-sm font-semibold text-slate-800 mb-3">
                技术架构
              </div>
              <div className="space-y-2 text-xs text-slate-500">
                <div>FastAPI</div>
                <div>LangGraph</div>
                <div>React 18</div>
                <div>Ant Design 5</div>
              </div>
            </div>
            <div>
              <div className="text-sm font-semibold text-slate-800 mb-3">
                支持模型
              </div>
              <div className="space-y-2 text-xs text-slate-500">
                <div>讯飞星火</div>
                <div>DeepSeek</div>
                <div>OpenAI</div>
                <div>智谱 AI</div>
              </div>
            </div>
          </div>
          <div className="pt-6 border-t border-slate-100 flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="text-sm text-slate-400">
              &copy; {new Date().getFullYear()} LearnLab
            </div>
            <div className="flex items-center gap-6 text-xs text-slate-400">
              <span>第十五届中国软件杯 A3 赛题</span>
              <span>基于大模型的个性化学习平台</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
