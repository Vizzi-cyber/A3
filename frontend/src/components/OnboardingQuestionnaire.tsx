import React, { useState } from "react";
import { Modal, Button, Radio, Slider, Typography, Space, Card } from "antd";
import {
  TrophyOutlined,
  RocketOutlined,
  BulbOutlined,
  CodeOutlined,
  BookOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
} from "@ant-design/icons";
import { onboardingApi } from "../services/api";
import type { OnboardingAnswers } from "../types";

const { Title, Text } = Typography;

interface OnboardingQuestionnaireProps {
  open: boolean;
  onComplete: () => void;
}

const steps = [
  { title: "基础水平", description: "了解你的C语言基础" },
  { title: "难度偏好", description: "选择适合你的难度" },
  { title: "学习时长", description: "规划每日学习时间" },
  { title: "学习目标", description: "明确你的目标" },
  { title: "学习风格", description: "选择学习方式" },
];

const OnboardingQuestionnaire: React.FC<OnboardingQuestionnaireProps> = ({
  open,
  onComplete,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [answers, setAnswers] = useState<OnboardingAnswers>({
    c_knowledge_level: 1,
    difficulty_preference: 5,
    daily_duration: 60,
    learning_goal: "skill_build",
    learning_style: "balanced",
  });

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      await onboardingApi.submit(answers);
      onComplete();
    } catch (e) {
      console.error("提交失败:", e);
    } finally {
      setLoading(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <div className="space-y-4">
            <Title level={5} className="!mb-4">
              你的C语言基础如何？
            </Title>
            <Radio.Group
              value={answers.c_knowledge_level}
              onChange={(e) =>
                setAnswers({ ...answers, c_knowledge_level: e.target.value })
              }
              className="w-full"
            >
              <Space direction="vertical" className="w-full">
                <Radio.Button
                  value={1}
                  className="w-full text-left h-auto !py-3"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-lg">🌱</span>
                    <div>
                      <div className="font-medium">完全零基础</div>
                      <div className="text-xs text-slate-400">
                        从未接触过编程
                      </div>
                    </div>
                  </div>
                </Radio.Button>
                <Radio.Button
                  value={2}
                  className="w-full text-left h-auto !py-3"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-lg">📖</span>
                    <div>
                      <div className="font-medium">了解基本概念</div>
                      <div className="text-xs text-slate-400">
                        知道变量、循环等概念
                      </div>
                    </div>
                  </div>
                </Radio.Button>
                <Radio.Button
                  value={3}
                  className="w-full text-left h-auto !py-3"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-lg">💻</span>
                    <div>
                      <div className="font-medium">写过简单程序</div>
                      <div className="text-xs text-slate-400">
                        能独立完成Hello World
                      </div>
                    </div>
                  </div>
                </Radio.Button>
                <Radio.Button
                  value={4}
                  className="w-full text-left h-auto !py-3"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-lg">🚀</span>
                    <div>
                      <div className="font-medium">有一定基础</div>
                      <div className="text-xs text-slate-400">
                        学过部分语法，做过小练习
                      </div>
                    </div>
                  </div>
                </Radio.Button>
                <Radio.Button
                  value={5}
                  className="w-full text-left h-auto !py-3"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-lg">⭐</span>
                    <div>
                      <div className="font-medium">比较熟悉</div>
                      <div className="text-xs text-slate-400">
                        想深入学习数据结构
                      </div>
                    </div>
                  </div>
                </Radio.Button>
              </Space>
            </Radio.Group>
          </div>
        );

      case 1:
        return (
          <div className="space-y-4">
            <Title level={5} className="!mb-4">
              你想要的学习难度？
            </Title>
            <div className="px-4">
              <Slider
                min={1}
                max={10}
                value={answers.difficulty_preference}
                onChange={(value) =>
                  setAnswers({ ...answers, difficulty_preference: value })
                }
                marks={{
                  1: "轻松",
                  5: "适中",
                  10: "挑战",
                }}
                tooltip={{ formatter: (v) => `${v}级` }}
              />
              <div className="flex justify-between mt-4">
                <Card
                  size="small"
                  className={`flex-1 mr-2 cursor-pointer transition-all ${
                    answers.difficulty_preference <= 3
                      ? "border-primary bg-primary/5"
                      : ""
                  }`}
                  onClick={() =>
                    setAnswers({ ...answers, difficulty_preference: 2 })
                  }
                >
                  <div className="text-center">
                    <div className="text-lg mb-1">😊</div>
                    <div className="text-xs font-medium">轻松入门</div>
                  </div>
                </Card>
                <Card
                  size="small"
                  className={`flex-1 mx-2 cursor-pointer transition-all ${
                    answers.difficulty_preference >= 4 &&
                    answers.difficulty_preference <= 6
                      ? "border-primary bg-primary/5"
                      : ""
                  }`}
                  onClick={() =>
                    setAnswers({ ...answers, difficulty_preference: 5 })
                  }
                >
                  <div className="text-center">
                    <div className="text-lg mb-1">💪</div>
                    <div className="text-xs font-medium">稳步提升</div>
                  </div>
                </Card>
                <Card
                  size="small"
                  className={`flex-1 ml-2 cursor-pointer transition-all ${
                    answers.difficulty_preference >= 7
                      ? "border-primary bg-primary/5"
                      : ""
                  }`}
                  onClick={() =>
                    setAnswers({ ...answers, difficulty_preference: 8 })
                  }
                >
                  <div className="text-center">
                    <div className="text-lg mb-1">🔥</div>
                    <div className="text-xs font-medium">挑战极限</div>
                  </div>
                </Card>
              </div>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-4">
            <Title level={5} className="!mb-4">
              每天计划学习多长时间？
            </Title>
            <Radio.Group
              value={answers.daily_duration}
              onChange={(e) =>
                setAnswers({ ...answers, daily_duration: e.target.value })
              }
              className="w-full"
            >
              <div className="grid grid-cols-2 gap-3">
                <Radio.Button value={30} className="!h-auto !py-4 text-left">
                  <div className="flex items-center gap-2">
                    <PlayCircleOutlined className="text-blue-500" />
                    <div>
                      <div className="font-medium">30分钟</div>
                      <div className="text-xs text-slate-400">碎片时间</div>
                    </div>
                  </div>
                </Radio.Button>
                <Radio.Button value={60} className="!h-auto !py-4 text-left">
                  <div className="flex items-center gap-2">
                    <BookOutlined className="text-green-500" />
                    <div>
                      <div className="font-medium">1小时</div>
                      <div className="text-xs text-slate-400">规律学习</div>
                    </div>
                  </div>
                </Radio.Button>
                <Radio.Button value={90} className="!h-auto !py-4 text-left">
                  <div className="flex items-center gap-2">
                    <CodeOutlined className="text-purple-500" />
                    <div>
                      <div className="font-medium">1.5小时</div>
                      <div className="text-xs text-slate-400">深度学习</div>
                    </div>
                  </div>
                </Radio.Button>
                <Radio.Button value={120} className="!h-auto !py-4 text-left">
                  <div className="flex items-center gap-2">
                    <RocketOutlined className="text-orange-500" />
                    <div>
                      <div className="font-medium">2小时+</div>
                      <div className="text-xs text-slate-400">集中突破</div>
                    </div>
                  </div>
                </Radio.Button>
              </div>
            </Radio.Group>
          </div>
        );

      case 3:
        return (
          <div className="space-y-4">
            <Title level={5} className="!mb-4">
              你的学习目标是？
            </Title>
            <Radio.Group
              value={answers.learning_goal}
              onChange={(e) =>
                setAnswers({ ...answers, learning_goal: e.target.value })
              }
              className="w-full"
            >
              <Space direction="vertical" className="w-full">
                <Radio.Button
                  value="exam_prep"
                  className="w-full text-left h-auto !py-3"
                >
                  <div className="flex items-center gap-3">
                    <TrophyOutlined className="text-yellow-500 text-lg" />
                    <div>
                      <div className="font-medium">考试备考</div>
                      <div className="text-xs text-slate-400">
                        为期末考试或等级考试做准备
                      </div>
                    </div>
                  </div>
                </Radio.Button>
                <Radio.Button
                  value="skill_build"
                  className="w-full text-left h-auto !py-3"
                >
                  <div className="flex items-center gap-3">
                    <CodeOutlined className="text-blue-500 text-lg" />
                    <div>
                      <div className="font-medium">技能提升</div>
                      <div className="text-xs text-slate-400">
                        系统学习C语言和数据结构
                      </div>
                    </div>
                  </div>
                </Radio.Button>
                <Radio.Button
                  value="project"
                  className="w-full text-left h-auto !py-3"
                >
                  <div className="flex items-center gap-3">
                    <RocketOutlined className="text-purple-500 text-lg" />
                    <div>
                      <div className="font-medium">项目实战</div>
                      <div className="text-xs text-slate-400">
                        为实际项目开发做准备
                      </div>
                    </div>
                  </div>
                </Radio.Button>
                <Radio.Button
                  value="exploration"
                  className="w-full text-left h-auto !py-3"
                >
                  <div className="flex items-center gap-3">
                    <BulbOutlined className="text-green-500 text-lg" />
                    <div>
                      <div className="font-medium">探索兴趣</div>
                      <div className="text-xs text-slate-400">
                        培养编程兴趣，拓宽视野
                      </div>
                    </div>
                  </div>
                </Radio.Button>
              </Space>
            </Radio.Group>
          </div>
        );

      case 4:
        return (
          <div className="space-y-4">
            <Title level={5} className="!mb-4">
              你更喜欢哪种学习方式？
            </Title>
            <Radio.Group
              value={answers.learning_style}
              onChange={(e) =>
                setAnswers({ ...answers, learning_style: e.target.value })
              }
              className="w-full"
            >
              <div className="grid grid-cols-3 gap-3">
                <Radio.Button
                  value="theory"
                  className="!h-auto !py-6 text-center"
                >
                  <div className="flex flex-col items-center gap-2">
                    <BookOutlined className="text-2xl text-blue-500" />
                    <div>
                      <div className="font-medium">理论优先</div>
                      <div className="text-xs text-slate-400">更多文档视频</div>
                    </div>
                  </div>
                </Radio.Button>
                <Radio.Button
                  value="practice"
                  className="!h-auto !py-6 text-center"
                >
                  <div className="flex flex-col items-center gap-2">
                    <CodeOutlined className="text-2xl text-green-500" />
                    <div>
                      <div className="font-medium">实战优先</div>
                      <div className="text-xs text-slate-400">更多代码练习</div>
                    </div>
                  </div>
                </Radio.Button>
                <Radio.Button
                  value="balanced"
                  className="!h-auto !py-6 text-center"
                >
                  <div className="flex flex-col items-center gap-2">
                    <CheckCircleOutlined className="text-2xl text-purple-500" />
                    <div>
                      <div className="font-medium">均衡发展</div>
                      <div className="text-xs text-slate-400">
                        理论+实践兼顾
                      </div>
                    </div>
                  </div>
                </Radio.Button>
              </div>
            </Radio.Group>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <Modal
      open={open}
      footer={null}
      closable={false}
      width={560}
      centered
      className="onboarding-modal"
    >
      <div className="py-4">
        {/* 进度条 */}
        <div className="mb-6">
          <div className="flex justify-between mb-2">
            <Text className="text-sm text-slate-500">
              步骤 {currentStep + 1} / {steps.length}
            </Text>
            <Text className="text-sm text-slate-500">
              {steps[currentStep].description}
            </Text>
          </div>
          <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-primary rounded-full transition-all duration-300"
              style={{
                width: `${((currentStep + 1) / steps.length) * 100}%`,
              }}
            />
          </div>
        </div>

        {/* 步骤内容 */}
        <div className="min-h-[280px]">{renderStepContent()}</div>

        {/* 按钮 */}
        <div className="flex justify-between mt-6">
          <Button
            onClick={handlePrev}
            disabled={currentStep === 0}
            className="rounded-lg"
          >
            上一步
          </Button>
          {currentStep < steps.length - 1 ? (
            <Button
              type="primary"
              onClick={handleNext}
              className="rounded-lg bg-primary"
            >
              下一步
            </Button>
          ) : (
            <Button
              type="primary"
              onClick={handleSubmit}
              loading={loading}
              className="rounded-lg bg-primary"
            >
              开始学习
            </Button>
          )}
        </div>
      </div>
    </Modal>
  );
};

export default OnboardingQuestionnaire;
