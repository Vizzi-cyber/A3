import { useState } from "react";
import {
  Card,
  Form,
  Input,
  Select,
  InputNumber,
  Button,
  Typography,
  Tag,
  Collapse,
  Spin,
  message,
  Empty,
  Row,
  Col,
  Statistic,
} from "antd";
import {
  FileTextOutlined,
  RocketOutlined,
  CheckCircleOutlined,
} from "@ant-design/icons";
import { teachingAssistApi } from "../../services/api";

const { Title, Text } = Typography;
const { TextArea } = Input;

interface QuizQuestion {
  id: number;
  type: string;
  difficulty: string;
  score: number;
  question: string;
  options?: string[];
  answer: string;
  explanation?: string;
  knowledge_point?: string;
  tags?: string[];
}

interface SmartQuizData {
  title?: string;
  subject?: string;
  total_score?: number;
  time_limit?: string;
  questions?: QuizQuestion[];
  difficulty_distribution?: Record<string, string>;
  knowledge_coverage?: string[];
  scoring_riders?: string;
  teaching_suggestions?: string;
  questions_text?: string;
  format?: string;
}

const DIFFICULTY_OPTIONS = [
  { value: "mixed", label: "混合难度" },
  { value: "basic", label: "基础题为主" },
  { value: "intermediate", label: "中等题为主" },
  { value: "advanced", label: "拔高题为主" },
];

const DIFFICULTY_COLOR: Record<string, string> = {
  basic: "green",
  intermediate: "blue",
  advanced: "red",
};

const TYPE_LABEL: Record<string, string> = {
  choice: "选择题",
  fill: "填空题",
  short_answer: "简答题",
  comprehensive: "综合题",
};

export default function SmartQuiz() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SmartQuizData | null>(null);

  const handleGenerate = async (values: {
    topic: string;
    knowledge_points?: string;
    difficulty?: string;
    count?: number;
  }) => {
    setLoading(true);
    try {
      const kps = values.knowledge_points
        ? values.knowledge_points
            .split(/[,，]/)
            .map((s) => s.trim())
            .filter(Boolean)
        : [];
      const res = await teachingAssistApi.generateSmartQuiz({
        topic: values.topic,
        knowledge_points: kps,
        difficulty: values.difficulty || "mixed",
        count: values.count || 5,
      });
      setResult(res.data.data);
      message.success("试卷生成成功");
    } catch {
      message.error("生成失败，请稍后重试");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Hero Header */}
      <div className="bg-gradient-to-r from-blue-500 to-indigo-600 rounded-2xl p-6 text-white">
        <div className="flex items-center gap-3 mb-1">
          <FileTextOutlined className="text-2xl" />
          <Title level={4} className="!text-white !m-0">
            AI智能组卷
          </Title>
        </div>
        <Text className="text-blue-100 text-sm">
          输入主题和知识点，AI自动生成高质量试卷
        </Text>
      </div>

      {/* Form */}
      <Card className="rounded-2xl border-0 shadow-sm">
        <Form form={form} layout="vertical" onFinish={handleGenerate}>
          <Row gutter={20}>
            <Col xs={24} lg={12}>
              <Form.Item
                name="topic"
                label="教学主题"
                rules={[{ required: true, message: "请输入教学主题" }]}
                tooltip="输入章节或知识点主题，AI将围绕此主题生成试卷"
              >
                <Input
                  placeholder="例如：C语言指针基础、第二章课后练习"
                  size="large"
                />
              </Form.Item>
            </Col>
            <Col xs={24} lg={12}>
              <Form.Item
                name="knowledge_points"
                label="知识点（逗号分隔）"
                tooltip="可选，指定具体考查的知识点范围，留空则由AI自动覆盖"
              >
                <TextArea
                  placeholder="例如：指针定义, 指针运算, 指针与数组（可选）"
                  autoSize={{ minRows: 1, maxRows: 3 }}
                  size="large"
                />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={20}>
            <Col xs={24} lg={12}>
              <Form.Item
                name="difficulty"
                label="难度要求"
                initialValue="mixed"
              >
                <Select size="large" options={DIFFICULTY_OPTIONS} />
              </Form.Item>
            </Col>
            <Col xs={24} lg={12}>
              <Form.Item name="count" label="题目数量" initialValue={5}>
                <InputNumber min={1} max={20} size="large" className="w-full" />
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
              智能组卷
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {/* Loading */}
      {loading && (
        <Card className="rounded-2xl border-0 shadow-sm text-center py-12">
          <Spin size="large" />
          <div className="mt-4">
            <Text type="secondary">AI正在生成试卷，请稍候...</Text>
          </div>
        </Card>
      )}

      {/* Result */}
      {result && !loading && (
        <div className="space-y-6">
          {/* Markdown fallback */}
          {result.format === "markdown" && result.questions_text ? (
            <Card
              className="rounded-2xl border-0 shadow-sm"
              title={result.title || "智能试卷"}
            >
              <pre className="whitespace-pre-wrap">{result.questions_text}</pre>
            </Card>
          ) : (
            <>
              {/* Quiz Header */}
              <Card className="rounded-2xl border-0 shadow-sm">
                <Title level={4}>{result.title || "智能试卷"}</Title>
                <div className="flex flex-wrap gap-4 mt-3">
                  {result.total_score && (
                    <Statistic
                      title="总分"
                      value={result.total_score}
                      suffix="分"
                    />
                  )}
                  {result.time_limit && (
                    <Statistic title="时限" value={result.time_limit} />
                  )}
                  {result.questions && (
                    <Statistic
                      title="题目数"
                      value={result.questions.length}
                      suffix="题"
                    />
                  )}
                </div>
                {result.difficulty_distribution && (
                  <div className="flex flex-wrap gap-2 mt-3">
                    {Object.entries(result.difficulty_distribution).map(
                      ([k, v]) => (
                        <Tag key={k} color={DIFFICULTY_COLOR[k] || "default"}>
                          {k === "basic"
                            ? "基础"
                            : k === "intermediate"
                              ? "中等"
                              : "拔高"}
                          ：{v}
                        </Tag>
                      ),
                    )}
                  </div>
                )}
              </Card>

              {/* Questions */}
              {result.questions && result.questions.length > 0 && (
                <Card
                  className="rounded-2xl border-0 shadow-sm"
                  title="题目列表"
                >
                  <Collapse
                    accordion
                    items={result.questions.map((q) => ({
                      key: q.id,
                      label: (
                        <div className="flex items-center gap-2 flex-wrap">
                          <Text strong>第{q.id}题</Text>
                          <Tag>{TYPE_LABEL[q.type] || q.type}</Tag>
                          <Tag
                            color={DIFFICULTY_COLOR[q.difficulty] || "default"}
                          >
                            {q.difficulty === "basic"
                              ? "基础"
                              : q.difficulty === "intermediate"
                                ? "中等"
                                : "拔高"}
                          </Tag>
                          <Tag color="blue">{q.score}分</Tag>
                        </div>
                      ),
                      children: (
                        <div className="space-y-3">
                          <div className="text-base">{q.question}</div>

                          {q.options && q.options.length > 0 && (
                            <div className="space-y-1">
                              {q.options.map((opt, i) => {
                                const isCorrect =
                                  opt.startsWith(q.answer) ||
                                  opt.charAt(0) === q.answer.charAt(0);
                                return (
                                  <div
                                    key={i}
                                    className={`p-2 rounded ${isCorrect ? "bg-green-50 border border-green-200" : "bg-gray-50"}`}
                                  >
                                    <Text
                                      className={
                                        isCorrect
                                          ? "text-green-700 font-medium"
                                          : ""
                                      }
                                    >
                                      {opt}
                                    </Text>
                                    {isCorrect && (
                                      <CheckCircleOutlined className="ml-2 text-green-500" />
                                    )}
                                  </div>
                                );
                              })}
                            </div>
                          )}

                          <div>
                            <Tag color="green">答案：{q.answer}</Tag>
                          </div>

                          {q.explanation && (
                            <div className="bg-blue-50 p-3 rounded">
                              <Text type="secondary" className="text-sm">
                                <strong>解析：</strong>
                                {q.explanation}
                              </Text>
                            </div>
                          )}

                          {q.knowledge_point && (
                            <Tag color="purple">
                              知识点：{q.knowledge_point}
                            </Tag>
                          )}
                        </div>
                      ),
                    }))}
                  />
                </Card>
              )}

              {/* Teaching Suggestions */}
              {result.teaching_suggestions && (
                <Card
                  className="rounded-2xl border-0 shadow-sm"
                  title="教学建议"
                >
                  <Text>{result.teaching_suggestions}</Text>
                </Card>
              )}
            </>
          )}
        </div>
      )}

      {/* Empty State */}
      {!result && !loading && (
        <Card className="rounded-2xl border-0 shadow-sm py-12">
          <Empty description="输入主题和知识点，AI自动生成试卷">
            <div className="flex gap-4 justify-center mt-4">
              <div className="text-center">
                <FileTextOutlined className="text-2xl text-blue-500" />
                <div className="text-sm mt-1">多题型</div>
              </div>
              <div className="text-center">
                <CheckCircleOutlined className="text-2xl text-green-500" />
                <div className="text-sm mt-1">自动评分</div>
              </div>
              <div className="text-center">
                <RocketOutlined className="text-2xl text-blue-500" />
                <div className="text-sm mt-1">智能难度</div>
              </div>
            </div>
          </Empty>
        </Card>
      )}
    </div>
  );
}
