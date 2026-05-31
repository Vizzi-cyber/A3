import React, { useEffect, useState } from "react";
import { Card, Button, Progress, Tag, Spin, Space } from "antd";
import {
  GiftOutlined,
  RocketOutlined,
  CheckCircleOutlined,
  FireOutlined,
} from "@ant-design/icons";
import { gamificationApi } from "../services/api";
import { useAppStore } from "../store";
import { useNavigate } from "react-router-dom";

interface ChallengeItem {
  id: string;
  title: string;
  description: string;
  reward: number;
  progress: number;
  completed: boolean;
}

const DailyChallenge: React.FC = () => {
  const [challenges, setChallenges] = useState<ChallengeItem[]>([]);
  const [loading, setLoading] = useState(false);
  const studentId = useAppStore((s) => s.studentId);
  const navigate = useNavigate();

  useEffect(() => {
    let ignore = false;
    const load = async () => {
      setLoading(true);
      try {
        const res = await gamificationApi.getTasks(studentId);
        if (!ignore) {
          const items = (res.data?.data || []).slice(0, 4).map((t) => ({
            id: t.task_id,
            title: t.title,
            description: t.description || "",
            reward: t.reward_points || 0,
            progress: t.progress || 0,
            completed: !!t.completed,
          }));
          setChallenges(items);
        }
      } catch {
        if (!ignore) setChallenges([]);
      } finally {
        if (!ignore) setLoading(false);
      }
    };
    load();
    return () => {
      ignore = true;
    };
  }, [studentId]);

  const incomplete = challenges.filter((c) => !c.completed);
  const completedCount = challenges.filter((c) => c.completed).length;
  const totalReward = incomplete.reduce((s, c) => s + c.reward, 0);

  return (
    <Card
      className="border border-slate-100 rounded-2xl shadow-card"
      title={
        <Space>
          <RocketOutlined className="text-indigo-500 text-lg" />
          <span className="font-semibold text-slate-800">每日微挑战</span>
        </Space>
      }
      extra={
        <Tag className="rounded-full border-0 bg-amber-50 text-amber-600 text-xs font-medium">
          <FireOutlined className="mr-1" />+{totalReward} XP 待领取
        </Tag>
      }
      styles={{ body: { padding: "20px" } }}
    >
      <Spin spinning={loading}>
        {challenges.length === 0 && !loading ? (
          <div className="text-center py-6 text-slate-400 text-sm">
            暂无挑战任务
          </div>
        ) : (
          <div className="space-y-3">
            {challenges.map((c) => (
              <div
                key={c.id}
                className={`flex items-center gap-4 p-4 rounded-xl border transition-all ${
                  c.completed
                    ? "bg-slate-50 border-slate-100 opacity-60"
                    : "bg-white border-slate-200 hover:border-indigo-300 hover:shadow-sm cursor-pointer"
                }`}
                onClick={() => {
                  if (!c.completed) navigate("/learning-path");
                }}
              >
                <div
                  className={`w-10 h-10 rounded-xl flex items-center justify-center text-white text-lg shrink-0 ${
                    c.completed
                      ? "bg-slate-300"
                      : "bg-gradient-to-br from-indigo-500 to-purple-500"
                  }`}
                >
                  {c.completed ? <CheckCircleOutlined /> : <GiftOutlined />}
                </div>
                <div className="flex-1 min-w-0">
                  <div
                    className={`text-sm font-medium ${c.completed ? "text-slate-400 line-through" : "text-slate-800"}`}
                  >
                    {c.title}
                  </div>
                  {c.description && (
                    <div className="text-xs text-slate-400 mt-0.5 truncate">
                      {c.description}
                    </div>
                  )}
                  {!c.completed && c.progress > 0 && (
                    <Progress
                      percent={Math.round(c.progress * 100)}
                      size="small"
                      strokeColor="#6366f1"
                      trailColor="#f1f5f9"
                      className="mt-1"
                    />
                  )}
                </div>
                <Tag
                  className={`rounded-full border-0 text-xs shrink-0 ${
                    c.completed
                      ? "bg-slate-100 text-slate-400"
                      : "bg-indigo-50 text-indigo-600 font-bold"
                  }`}
                >
                  +{c.reward} XP
                </Tag>
              </div>
            ))}

            <div className="flex items-center justify-between pt-2">
              <span className="text-xs text-slate-400">
                已完成 {completedCount}/{challenges.length}
              </span>
              <Button
                type="link"
                size="small"
                className="text-primary text-xs"
                onClick={() => navigate("/learning-path")}
              >
                查看全部任务
              </Button>
            </div>
          </div>
        )}
      </Spin>
    </Card>
  );
};

export default React.memo(DailyChallenge);
