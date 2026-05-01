import React, { useEffect, useState } from "react";
import { Card, Segmented, List, Avatar, Tag, Space, Spin } from "antd";
import {
  TrophyOutlined,
  CrownOutlined,
  FireOutlined,
  UserOutlined,
} from "@ant-design/icons";
import { gamificationApi } from "../services/api";
import { useAppStore } from "../store";
import type { LeaderboardEntry } from "../types";

const periodOptions = [
  { label: "今日", value: "daily" },
  { label: "本周", value: "weekly" },
  { label: "本月", value: "monthly" },
];

const medalColors = ["#f59e0b", "#94a3b8", "#cd7f32"];

const Leaderboard: React.FC<{ compact?: boolean }> = ({ compact = false }) => {
  const [period, setPeriod] = useState<string>("weekly");
  const [data, setData] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const studentId = useAppStore((s) => s.studentId);

  useEffect(() => {
    let ignore = false;
    const load = async () => {
      setLoading(true);
      try {
        const res = await gamificationApi.getLeaderboard(
          period,
          compact ? 5 : 10,
        );
        if (!ignore) setData(res.data?.data || []);
      } catch {
        if (!ignore) setData([]);
      } finally {
        if (!ignore) setLoading(false);
      }
    };
    load();
    return () => {
      ignore = true;
    };
  }, [period, compact]);

  return (
    <Card
      className="border border-slate-100 rounded-2xl shadow-card"
      title={
        <Space>
          <TrophyOutlined className="text-amber-500 text-lg" />
          <span className="font-semibold text-slate-800">排行榜</span>
        </Space>
      }
      extra={
        <Segmented
          options={periodOptions}
          value={period}
          onChange={(val) => setPeriod(val as string)}
          size="small"
        />
      }
      styles={{ body: { padding: compact ? "16px" : "24px" } }}
    >
      <Spin spinning={loading}>
        {data.length === 0 && !loading ? (
          <div className="text-center py-8 text-slate-400 text-sm">
            暂无排行数据
          </div>
        ) : (
          <List
            dataSource={data}
            renderItem={(item, idx) => {
              const isMe = item.student_id === studentId;
              const isTop3 = idx < 3;
              return (
                <List.Item
                  className={`rounded-xl px-3 py-2 mb-1 transition-all ${
                    isMe
                      ? "bg-indigo-50 border border-indigo-200"
                      : "hover:bg-slate-50"
                  }`}
                  style={{ border: isMe ? undefined : "1px solid transparent" }}
                >
                  <List.Item.Meta
                    avatar={
                      isTop3 ? (
                        <div
                          className="w-9 h-9 rounded-full flex items-center justify-center text-white text-lg font-bold shrink-0"
                          style={{ background: medalColors[idx] }}
                        >
                          <CrownOutlined />
                        </div>
                      ) : (
                        <Avatar
                          size={36}
                          icon={<UserOutlined />}
                          className={isMe ? "bg-primary" : "bg-slate-200"}
                        />
                      )
                    }
                    title={
                      <div className="flex items-center gap-2">
                        <span
                          className={`text-sm font-medium ${isMe ? "text-primary" : "text-slate-800"}`}
                        >
                          {item.username || item.student_id}
                          {isMe && (
                            <Tag className="ml-1 rounded-full border-0 bg-primary-50 text-primary text-xs">
                              我
                            </Tag>
                          )}
                        </span>
                      </div>
                    }
                    description={
                      <Space size={12}>
                        <span className="text-xs text-slate-500">
                          第{" "}
                          <span className="font-bold text-slate-700">
                            {item.rank || idx + 1}
                          </span>{" "}
                          名
                        </span>
                        {item.streak_days !== undefined &&
                          item.streak_days > 0 && (
                            <span className="text-xs text-orange-500 flex items-center gap-0.5">
                              <FireOutlined /> {item.streak_days}天
                            </span>
                          )}
                      </Space>
                    }
                  />
                  <div className="text-right">
                    <div className="text-base font-bold text-primary">
                      {item.points}
                    </div>
                    <div className="text-xs text-slate-400">XP</div>
                  </div>
                </List.Item>
              );
            }}
          />
        )}
      </Spin>
    </Card>
  );
};

export default Leaderboard;
