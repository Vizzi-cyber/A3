import { useState } from "react";
import {
  Card,
  Button,
  Typography,
  Tag,
  Spin,
  message,
  Empty,
  Row,
  Col,
  Alert,
} from "antd";
import {
  LineChartOutlined,
  BulbOutlined,
  StarOutlined,
  WarningOutlined,
  RocketOutlined,
} from "@ant-design/icons";
import ReactMarkdown from "react-markdown";
import { teachingAssistApi } from "../../services/api";

const { Title, Text, Paragraph } = Typography;

interface InsightSection {
  title: string;
  content: string;
  data_highlights?: string[];
  icon?: string;
}

interface InsightRecommendation {
  target: string;
  action: string;
  priority: "high" | "medium" | "low";
}

interface InsightsData {
  title?: string;
  date?: string;
  overview?: string;
  sections?: InsightSection[];
  key_findings?: string[];
  recommendations?: InsightRecommendation[];
  risk_students?: string[];
  star_students?: string[];
  mood?: "positive" | "neutral" | "concerned";
  narrative?: string;
  format?: string;
}

const MOOD_CONFIG = {
  positive: { color: "green", label: "积极" },
  neutral: { color: "blue", label: "平稳" },
  concerned: { color: "orange", label: "需关注" },
};

const PRIORITY_CONFIG = {
  high: { color: "red", label: "高" },
  medium: { color: "orange", label: "中" },
  low: { color: "blue", label: "低" },
};

export default function LearningInsights() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<InsightsData | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const res = await teachingAssistApi.generateInsights();
      setResult(res.data.data);
      message.success("学情洞察报告生成成功");
    } catch {
      message.error("生成失败，请稍后重试");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Hero Header */}
      <div className="bg-gradient-to-r from-amber-500 to-orange-600 rounded-2xl p-6 text-white">
        <div className="flex items-center gap-3 mb-1">
          <LineChartOutlined className="text-2xl" />
          <Title level={4} className="!text-white !m-0">
            AI学情洞察
          </Title>
        </div>
        <Text className="text-amber-100 text-sm">
          基于班级学习数据，AI自动生成叙事化学情分析报告
        </Text>
      </div>

      {/* Generate Button */}
      {!result && !loading && (
        <Card className="rounded-2xl border-0 shadow-sm py-8">
          <Empty description="一键生成班级学情洞察报告">
            <Button
              type="primary"
              size="large"
              icon={<RocketOutlined />}
              onClick={handleGenerate}
              className="bg-[#0052ff] rounded-xl px-8"
            >
              生成洞察报告
            </Button>
          </Empty>
        </Card>
      )}

      {/* Loading */}
      {loading && (
        <Card className="rounded-2xl border-0 shadow-sm text-center py-12">
          <Spin size="large" />
          <div className="mt-4">
            <Text type="secondary">AI正在分析班级数据并生成报告...</Text>
          </div>
        </Card>
      )}

      {/* Result */}
      {result && !loading && (
        <div className="space-y-6">
          {/* Markdown fallback */}
          {result.format === "markdown" && result.narrative ? (
            <Card
              className="rounded-2xl border-0 shadow-sm"
              title={result.title || "学情洞察报告"}
            >
              <ReactMarkdown>{result.narrative}</ReactMarkdown>
            </Card>
          ) : (
            <>
              {/* Title & Mood */}
              <Card className="rounded-2xl border-0 shadow-sm">
                <div className="flex items-center justify-between">
                  <div>
                    <Title level={4}>{result.title || "学情洞察报告"}</Title>
                    {result.date && <Text type="secondary">{result.date}</Text>}
                  </div>
                  {result.mood && (
                    <Tag
                      color={MOOD_CONFIG[result.mood]?.color}
                      className="text-base px-3 py-1"
                    >
                      班级状态：{MOOD_CONFIG[result.mood]?.label}
                    </Tag>
                  )}
                </div>
                {result.overview && (
                  <Paragraph className="mt-4 text-base">
                    {result.overview}
                  </Paragraph>
                )}
              </Card>

              {/* Key Findings */}
              {result.key_findings && result.key_findings.length > 0 && (
                <Card
                  className="rounded-2xl border-0 shadow-sm"
                  title={
                    <>
                      <BulbOutlined className="mr-2" />
                      核心发现
                    </>
                  }
                >
                  <ol className="list-decimal pl-4 space-y-2">
                    {result.key_findings.map((finding, i) => (
                      <li key={i}>
                        <Text className="text-base">{finding}</Text>
                      </li>
                    ))}
                  </ol>
                </Card>
              )}

              {/* Sections */}
              {result.sections && result.sections.length > 0 && (
                <div className="space-y-4">
                  {result.sections.map((section, i) => (
                    <Card
                      key={i}
                      className="rounded-2xl border-0 shadow-sm"
                      title={section.title}
                    >
                      <ReactMarkdown>{section.content}</ReactMarkdown>
                      {section.data_highlights &&
                        section.data_highlights.length > 0 && (
                          <div className="flex flex-wrap gap-2 mt-3">
                            {section.data_highlights.map((h, j) => (
                              <Tag key={j} color="blue">
                                {h}
                              </Tag>
                            ))}
                          </div>
                        )}
                    </Card>
                  ))}
                </div>
              )}

              {/* Star & Risk Students */}
              <Row gutter={[20, 20]}>
                {result.star_students && result.star_students.length > 0 && (
                  <Col xs={24} lg={12}>
                    <Card
                      className="rounded-2xl border-0 shadow-sm"
                      title={
                        <>
                          <StarOutlined className="mr-2 text-yellow-500" />
                          表现优秀
                        </>
                      }
                    >
                      <div className="flex flex-wrap gap-2">
                        {result.star_students.map((s, i) => (
                          <Tag
                            key={i}
                            color="gold"
                            className="text-sm px-3 py-1"
                          >
                            {s}
                          </Tag>
                        ))}
                      </div>
                    </Card>
                  </Col>
                )}
                {result.risk_students && result.risk_students.length > 0 && (
                  <Col xs={24} lg={12}>
                    <Card
                      className="rounded-2xl border-0 shadow-sm"
                      title={
                        <>
                          <WarningOutlined className="mr-2 text-red-500" />
                          需要关注
                        </>
                      }
                    >
                      <div className="flex flex-wrap gap-2">
                        {result.risk_students.map((s, i) => (
                          <Tag
                            key={i}
                            color="red"
                            className="text-sm px-3 py-1"
                          >
                            {s}
                          </Tag>
                        ))}
                      </div>
                    </Card>
                  </Col>
                )}
              </Row>

              {/* Recommendations */}
              {result.recommendations && result.recommendations.length > 0 && (
                <Card
                  className="rounded-2xl border-0 shadow-sm"
                  title={
                    <>
                      <BulbOutlined className="mr-2" />
                      教学建议
                    </>
                  }
                >
                  <div className="space-y-3">
                    {result.recommendations.map((rec, i) => (
                      <Alert
                        key={i}
                        message={
                          <div>
                            <Text strong>{rec.target}：</Text>
                            <Text>{rec.action}</Text>
                          </div>
                        }
                        type={
                          rec.priority === "high"
                            ? "error"
                            : rec.priority === "medium"
                              ? "warning"
                              : "info"
                        }
                        showIcon
                        icon={
                          rec.priority === "high" ? (
                            <WarningOutlined />
                          ) : (
                            <BulbOutlined />
                          )
                        }
                      />
                    ))}
                  </div>
                </Card>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
