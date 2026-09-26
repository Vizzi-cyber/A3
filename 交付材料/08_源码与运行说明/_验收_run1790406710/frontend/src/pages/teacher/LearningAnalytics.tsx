import React, { useEffect, useState } from "react";
import {
  Card,
  Row,
  Col,
  Typography,
  Statistic,
  Table,
  Tag,
  Progress,
  Button,
  Select,
} from "antd";
import {
  RiseOutlined,
  FallOutlined,
  AlertOutlined,
  BulbOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import { teacherApi } from "../../services/api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const LearningAnalytics: React.FC = () => {
  const [weakPoints, setWeakPoints] = useState<
    { tag: string; count: number }[]
  >([]);
  const [weakAreas, setWeakAreas] = useState<{ area: string; count: number }[]>(
    [],
  );
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await teacherApi.getWeakPoints();
      setWeakPoints(res.data.weak_tags || []);
      setWeakAreas(res.data.weak_areas || []);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const chartData = weakPoints.slice(0, 8).map((item) => ({
    name: item.tag,
    count: item.count,
  }));

  // 根据真实数据生成洞察
  const totalWeakStudents = weakAreas.reduce((sum, a) => sum + a.count, 0);
  const topWeakArea = weakAreas.length > 0 ? weakAreas[0].area : "暂无";
  const topWeakCount = weakAreas.length > 0 ? weakAreas[0].count : 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Typography.Title level={4} className="!m-0">
          学情分析
        </Typography.Title>
        <Button icon={<ReloadOutlined />} onClick={loadData}>
          刷新
        </Button>
      </div>

      <Row gutter={[20, 20]}>
        {/* 薄弱知识点分布 */}
        <Col xs={24} lg={14}>
          <Card
            className="rounded-2xl border-0 shadow-sm"
            title="薄弱知识点分布"
          >
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis
                    dataKey="name"
                    tick={{ fill: "#64748b", fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fill: "#64748b" }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip
                    contentStyle={{
                      borderRadius: 12,
                      border: "none",
                      boxShadow: "0 4px 12px rgba(0,0,0,0.06)",
                    }}
                  />
                  <Bar dataKey="count" fill="#0052ff" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>

        {/* 薄弱领域统计 */}
        <Col xs={24} lg={10}>
          <Card className="rounded-2xl border-0 shadow-sm" title="薄弱领域">
            <div className="space-y-4">
              {weakAreas.length ? (
                weakAreas.slice(0, 8).map((item, idx) => (
                  <div key={idx} className="flex items-center gap-3">
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium text-slate-700">
                          {item.area}
                        </span>
                        <span className="text-xs text-slate-400">
                          {item.count}人
                        </span>
                      </div>
                      <Progress
                        percent={Math.min(100, (item.count / 20) * 100)}
                        showInfo={false}
                        strokeColor={
                          item.count > 5
                            ? "#ef4444"
                            : item.count > 2
                              ? "#f59e0b"
                              : "#10b981"
                        }
                      />
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-slate-400 text-sm py-8 text-center">
                  暂无数据
                </div>
              )}
            </div>
          </Card>
        </Col>
      </Row>

      {/* 学情洞察 */}
      <Card className="rounded-2xl border-0 shadow-sm" title="学情洞察">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-100">
            <div className="flex items-center gap-2 mb-2">
              <RiseOutlined className="text-emerald-500" />
              <span className="font-medium text-emerald-700">薄弱领域</span>
            </div>
            <p className="text-sm text-emerald-600 m-0">
              共有{totalWeakStudents}人次存在薄弱领域，主要集中在"{topWeakArea}
              "，建议重点关注。
            </p>
          </div>
          <div className="p-4 rounded-xl bg-amber-50 border border-amber-100">
            <div className="flex items-center gap-2 mb-2">
              <AlertOutlined className="text-amber-500" />
              <span className="font-medium text-amber-700">重点关注</span>
            </div>
            <p className="text-sm text-amber-600 m-0">
              "{topWeakArea}"有{topWeakCount}
              人薄弱，建议增加该部分的讲解和练习。
            </p>
          </div>
          <div className="p-4 rounded-xl bg-blue-50 border border-blue-100">
            <div className="flex items-center gap-2 mb-2">
              <BulbOutlined className="text-blue-500" />
              <span className="font-medium text-blue-700">教学建议</span>
            </div>
            <p className="text-sm text-blue-600 m-0">
              {weakAreas.length > 0
                ? `薄弱领域共${weakAreas.length}个，建议制定针对性教学计划。`
                : "暂无足够数据生成建议，继续收集学习数据。"}
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default LearningAnalytics;
