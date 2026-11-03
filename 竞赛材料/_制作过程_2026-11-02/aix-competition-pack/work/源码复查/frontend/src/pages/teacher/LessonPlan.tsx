import { useState } from "react";
import {
  Card,
  Form,
  Input,
  Select,
  Button,
  Typography,
  Tag,
  Collapse,
  Progress,
  Spin,
  message,
  Empty,
  Row,
  Col,
  Statistic,
} from "antd";
import {
  BookOutlined,
  ThunderboltOutlined,
  BulbOutlined,
  RocketOutlined,
  ClockCircleOutlined,
} from "@ant-design/icons";
import ReactMarkdown from "react-markdown";
import { teachingAssistApi } from "../../services/api";

const { Title, Text, Paragraph } = Typography;

const STYLES = [
  { value: "探究式", label: "探究式 — 以问题驱动，引导学生自主发现" },
  { value: "讲授式", label: "讲授式 — 系统讲解，注重知识传递效率" },
  { value: "翻转课堂", label: "翻转课堂 — 课前预习+课中讨论+课后巩固" },
  { value: "项目式", label: "项目式 — 以真实项目为载体，学以致用" },
];

interface LessonPlanData {
  title?: string;
  teaching_objectives?: {
    knowledge?: string[];
    ability?: string[];
    emotion?: string[];
  };
  key_points?: string[];
  difficult_points?: string[];
  teaching_process?: Array<{
    phase: string;
    duration: string;
    activities?: string[];
    teacher_behavior?: string;
    student_behavior?: string;
  }>;
  methods?: string[];
  time_distribution?: Record<string, number>;
  board_design?: string;
  reflection_hints?: string[];
  resources_needed?: string[];
  plan_text?: string;
  format?: string;
}

export default function LessonPlan() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<LessonPlanData | null>(null);

  const handleGenerate = async (values: { topic: string; style: string }) => {
    setLoading(true);
    try {
      const res = await teachingAssistApi.generateLessonPlan(values);
      setResult(res.data.data);
      message.success("备课方案生成成功");
    } catch {
      message.error("生成失败，请稍后重试");
    } finally {
      setLoading(false);
    }
  };

  const totalTime = result?.time_distribution
    ? Object.values(result.time_distribution).reduce((a, b) => a + b, 0)
    : 0;

  return (
    <div className="space-y-6">
      {/* Hero Header */}
      <div className="bg-gradient-to-r from-sky-500 to-blue-600 rounded-2xl p-6 text-white">
        <div className="flex items-center gap-3 mb-1">
          <ThunderboltOutlined className="text-2xl" />
          <Title level={4} className="!text-white !m-0">
            AI智能备课
          </Title>
        </div>
        <Text className="text-sky-100 text-sm">
          输入教学主题，AI将为您生成完整的备课方案
        </Text>
      </div>

      {/* Form */}
      <Card className="rounded-2xl border-0 shadow-sm">
        <Form form={form} layout="vertical" onFinish={handleGenerate}>
          <Row gutter={20}>
            <Col xs={24} lg={14}>
              <Form.Item
                name="topic"
                label="教学主题"
                rules={[{ required: true, message: "请输入教学主题" }]}
                tooltip="输入章节名称或具体知识点，AI将据此生成完整备课方案"
              >
                <Input
                  placeholder="例如：C语言指针基础、数组与排序算法"
                  size="large"
                />
              </Form.Item>
            </Col>
            <Col xs={24} lg={10}>
              <Form.Item
                name="style"
                label="教学风格"
                initialValue="探究式"
                tooltip="不同风格会影响教学过程的设计方式"
              >
                <Select size="large" options={STYLES} />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              size="large"
              icon={<RocketOutlined />}
              className="bg-[#0052ff] rounded-xl px-8"
            >
              生成备课方案
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {/* Loading */}
      {loading && (
        <Card className="rounded-2xl border-0 shadow-sm text-center py-12">
          <Spin size="large" />
          <div className="mt-4">
            <Text type="secondary">AI正在生成备课方案，请稍候...</Text>
          </div>
        </Card>
      )}

      {/* Result */}
      {result && !loading && (
        <div className="space-y-6">
          {/* Markdown fallback */}
          {result.format === "markdown" && result.plan_text ? (
            <Card
              className="rounded-2xl border-0 shadow-sm"
              title={result.title || "备课方案"}
            >
              <ReactMarkdown>{result.plan_text}</ReactMarkdown>
            </Card>
          ) : (
            <>
              {/* Title & Overview */}
              <Card className="rounded-2xl border-0 shadow-sm">
                <Title level={4}>{result.title || "备课方案"}</Title>
                {result.methods && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    {result.methods.map((m, i) => (
                      <Tag key={i} color="blue">
                        {m}
                      </Tag>
                    ))}
                  </div>
                )}
              </Card>

              {/* Teaching Objectives */}
              {result.teaching_objectives && (
                <Card
                  className="rounded-2xl border-0 shadow-sm"
                  title={
                    <>
                      <BulbOutlined className="mr-2" />
                      教学目标
                    </>
                  }
                >
                  <Row gutter={[16, 16]}>
                    {result.teaching_objectives.knowledge && (
                      <Col xs={24} md={8}>
                        <div className="font-medium mb-2">知识目标</div>
                        {result.teaching_objectives.knowledge.map((item, i) => (
                          <Tag key={i} color="blue" className="mb-1">
                            {item}
                          </Tag>
                        ))}
                      </Col>
                    )}
                    {result.teaching_objectives.ability && (
                      <Col xs={24} md={8}>
                        <div className="font-medium mb-2">能力目标</div>
                        {result.teaching_objectives.ability.map((item, i) => (
                          <Tag key={i} color="green" className="mb-1">
                            {item}
                          </Tag>
                        ))}
                      </Col>
                    )}
                    {result.teaching_objectives.emotion && (
                      <Col xs={24} md={8}>
                        <div className="font-medium mb-2">情感目标</div>
                        {result.teaching_objectives.emotion.map((item, i) => (
                          <Tag key={i} color="orange" className="mb-1">
                            {item}
                          </Tag>
                        ))}
                      </Col>
                    )}
                  </Row>
                </Card>
              )}

              {/* Key & Difficult Points */}
              <Row gutter={[20, 20]}>
                {result.key_points && result.key_points.length > 0 && (
                  <Col xs={24} lg={12}>
                    <Card
                      className="rounded-2xl border-0 shadow-sm"
                      title="教学重点"
                    >
                      {result.key_points.map((item, i) => (
                        <div key={i} className="flex items-start gap-2 mb-2">
                          <Tag color="red">{i + 1}</Tag>
                          <Text>{item}</Text>
                        </div>
                      ))}
                    </Card>
                  </Col>
                )}
                {result.difficult_points &&
                  result.difficult_points.length > 0 && (
                    <Col xs={24} lg={12}>
                      <Card
                        className="rounded-2xl border-0 shadow-sm"
                        title="教学难点"
                      >
                        {result.difficult_points.map((item, i) => (
                          <div key={i} className="flex items-start gap-2 mb-2">
                            <Tag color="volcano">{i + 1}</Tag>
                            <Text>{item}</Text>
                          </div>
                        ))}
                      </Card>
                    </Col>
                  )}
              </Row>

              {/* Teaching Process */}
              {result.teaching_process &&
                result.teaching_process.length > 0 && (
                  <Card
                    className="rounded-2xl border-0 shadow-sm"
                    title={
                      <>
                        <ClockCircleOutlined className="mr-2" />
                        教学过程
                      </>
                    }
                  >
                    <Collapse
                      accordion
                      items={result.teaching_process.map((phase, i) => ({
                        key: i,
                        label: (
                          <div className="flex items-center gap-2">
                            <Tag color="blue">{phase.phase}</Tag>
                            <Text type="secondary">{phase.duration}</Text>
                          </div>
                        ),
                        children: (
                          <>
                            {phase.activities && (
                              <div className="mb-3">
                                <Text strong>活动：</Text>
                                <ul className="mt-1">
                                  {phase.activities.map((a, j) => (
                                    <li key={j}>{a}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            {phase.teacher_behavior && (
                              <div className="mb-2">
                                <Tag color="purple">教师</Tag>
                                <Text>{phase.teacher_behavior}</Text>
                              </div>
                            )}
                            {phase.student_behavior && (
                              <div>
                                <Tag color="cyan">学生</Tag>
                                <Text>{phase.student_behavior}</Text>
                              </div>
                            )}
                          </>
                        ),
                      }))}
                    />
                  </Card>
                )}

              {/* Time Distribution */}
              {result.time_distribution && totalTime > 0 && (
                <Card
                  className="rounded-2xl border-0 shadow-sm"
                  title="时间分配"
                >
                  <div className="space-y-3">
                    {Object.entries(result.time_distribution).map(
                      ([phase, minutes]) => (
                        <div key={phase}>
                          <div className="flex justify-between mb-1">
                            <Text>{phase}</Text>
                            <Text type="secondary">{minutes}分钟</Text>
                          </div>
                          <Progress
                            percent={Math.round((minutes / totalTime) * 100)}
                            strokeColor="#0052ff"
                            showInfo={false}
                          />
                        </div>
                      ),
                    )}
                    <div className="text-right">
                      <Text type="secondary">总计 {totalTime} 分钟</Text>
                    </div>
                  </div>
                </Card>
              )}

              {/* Board Design */}
              {result.board_design && (
                <Card
                  className="rounded-2xl border-0 shadow-sm"
                  title="板书设计"
                >
                  <ReactMarkdown>{result.board_design}</ReactMarkdown>
                </Card>
              )}

              {/* Reflection Hints */}
              {result.reflection_hints &&
                result.reflection_hints.length > 0 && (
                  <Card
                    className="rounded-2xl border-0 shadow-sm"
                    title="教学反思预设"
                  >
                    <ul className="list-disc pl-4">
                      {result.reflection_hints.map((hint, i) => (
                        <li key={i} className="mb-1">
                          <Text>{hint}</Text>
                        </li>
                      ))}
                    </ul>
                  </Card>
                )}

              {/* Resources */}
              {result.resources_needed &&
                result.resources_needed.length > 0 && (
                  <Card
                    className="rounded-2xl border-0 shadow-sm"
                    title="所需资源"
                  >
                    <div className="flex flex-wrap gap-2">
                      {result.resources_needed.map((r, i) => (
                        <Tag key={i}>{r}</Tag>
                      ))}
                    </div>
                  </Card>
                )}
            </>
          )}
        </div>
      )}

      {/* Empty State */}
      {!result && !loading && (
        <Card className="rounded-2xl border-0 shadow-sm py-12">
          <Empty description="输入教学主题，点击生成即可获得AI备课方案">
            <div className="flex gap-4 justify-center mt-4">
              <div className="text-center">
                <BulbOutlined className="text-2xl text-blue-500" />
                <div className="text-sm mt-1">智能目标</div>
              </div>
              <div className="text-center">
                <BookOutlined className="text-2xl text-green-500" />
                <div className="text-sm mt-1">结构化过程</div>
              </div>
              <div className="text-center">
                <ClockCircleOutlined className="text-2xl text-orange-500" />
                <div className="text-sm mt-1">时间分配</div>
              </div>
            </div>
          </Empty>
        </Card>
      )}
    </div>
  );
}
