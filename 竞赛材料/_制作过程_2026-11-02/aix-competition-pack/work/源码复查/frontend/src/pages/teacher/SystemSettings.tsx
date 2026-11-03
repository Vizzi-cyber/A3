import React, { useState, useEffect } from "react";
import {
  Card,
  Form,
  Input,
  Switch,
  Button,
  Typography,
  Divider,
  Space,
  Tag,
  Spin,
  message,
} from "antd";
import {
  SaveOutlined,
  UserOutlined,
  LockOutlined,
  BellOutlined,
  GlobalOutlined,
} from "@ant-design/icons";
import { useAppStore } from "../../store";
import { authApi, teacherApi } from "../../services/api";
import { extractApiError } from "../../utils/error";

interface SystemInfo {
  version: string;
  ai_model: string;
  database_status: string;
  last_updated: string;
}

const SystemSettings: React.FC = () => {
  const userInfo = useAppStore((s) => s.userInfo);
  const logout = useAppStore((s) => s.logout);
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [passwordSaving, setPasswordSaving] = useState(false);
  const [notifications, setNotifications] = useState({
    learningReminder: true,
    assignment: true,
    scoreAlert: true,
    dailySummary: false,
  });

  useEffect(() => {
    loadSystemInfo();
    try {
      const saved = localStorage.getItem("learnlab-teacher-notifications");
      if (saved) setNotifications(JSON.parse(saved));
    } catch {
      // Use the default preferences when an older or malformed value is present.
    }
  }, []);

  const loadSystemInfo = async () => {
    setLoading(true);
    try {
      const res = await teacherApi.getSystemInfo();
      if (res.data?.system_info) {
        setSystemInfo(res.data.system_info);
      }
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const saveNotifications = () => {
    setSaving(true);
    try {
      localStorage.setItem(
        "learnlab-teacher-notifications",
        JSON.stringify(notifications),
      );
      message.success("通知设置已保存");
    } catch {
      message.error("设置保存失败，请检查浏览器存储权限");
    } finally {
      setSaving(false);
    }
  };

  const clearCachedData = () => {
    Object.keys(localStorage)
      .filter((key) => key.startsWith("learnlab-cache-"))
      .forEach((key) => localStorage.removeItem(key));
    message.success("本地缓存已清除");
  };

  const resetNotifications = () => {
    setNotifications({
      learningReminder: true,
      assignment: true,
      scoreAlert: true,
      dailySummary: false,
    });
    message.info("通知设置已恢复默认，请保存后生效");
  };

  const handleLogout = () => {
    logout();
    window.location.assign("/login");
  };

  const changePassword = async (values: {
    currentPassword: string;
    newPassword: string;
    confirmPassword: string;
  }) => {
    setPasswordSaving(true);
    try {
      await authApi.changePassword({
        current_password: values.currentPassword,
        new_password: values.newPassword,
      });
      message.success("密码已更新，请使用新密码重新登录");
      window.setTimeout(handleLogout, 600);
    } catch (error) {
      message.error(extractApiError(error, "密码更新失败"));
    } finally {
      setPasswordSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <Typography.Title level={4} className="!m-0">
        系统设置
      </Typography.Title>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 账户信息 */}
        <Card className="rounded-2xl border-0 shadow-sm" title="账户信息">
          <Form layout="vertical" onFinish={changePassword} autoComplete="off">
            <Form.Item label="用户名">
              <Input
                prefix={<UserOutlined className="text-slate-400" />}
                value={userInfo?.username || ""}
                disabled
              />
            </Form.Item>
            <Form.Item label="角色">
              <Tag className="rounded-full" color="blue">
                教师
              </Tag>
            </Form.Item>
            <Divider />
            <Form.Item
              label="当前密码"
              name="currentPassword"
              rules={[{ required: true, message: "请输入当前密码" }]}
            >
              <Input.Password
                prefix={<LockOutlined className="text-slate-400" />}
                placeholder="请输入当前密码"
              />
            </Form.Item>
            <Form.Item
              label="新密码"
              name="newPassword"
              rules={[
                { required: true, message: "请输入新密码" },
                { min: 8, message: "新密码至少需要 8 位" },
                {
                  pattern: /[A-Za-z]/,
                  message: "新密码至少包含一个字母",
                },
                { pattern: /\d/, message: "新密码至少包含一个数字" },
              ]}
            >
              <Input.Password
                prefix={<LockOutlined className="text-slate-400" />}
                placeholder="至少 8 位，包含字母和数字"
              />
            </Form.Item>
            <Form.Item
              label="确认新密码"
              name="confirmPassword"
              dependencies={["newPassword"]}
              rules={[
                { required: true, message: "请再次输入新密码" },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    return !value || getFieldValue("newPassword") === value
                      ? Promise.resolve()
                      : Promise.reject(new Error("两次输入的新密码不一致"));
                  },
                }),
              ]}
            >
              <Input.Password
                prefix={<LockOutlined className="text-slate-400" />}
                placeholder="再次输入新密码"
              />
            </Form.Item>
            <Button htmlType="submit" loading={passwordSaving} block>
              更新密码
            </Button>
          </Form>
        </Card>

        {/* 通知设置 */}
        <Card className="rounded-2xl border-0 shadow-sm" title="通知设置">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-slate-800">学习提醒</div>
                <div className="text-sm text-slate-400">
                  学生长时间未学习时通知
                </div>
              </div>
              <Switch
                checked={notifications.learningReminder}
                onChange={(checked) =>
                  setNotifications((current) => ({
                    ...current,
                    learningReminder: checked,
                  }))
                }
              />
            </div>
            <Divider />
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-slate-800">作业提交通知</div>
                <div className="text-sm text-slate-400">学生提交作业时通知</div>
              </div>
              <Switch
                checked={notifications.assignment}
                onChange={(checked) =>
                  setNotifications((current) => ({
                    ...current,
                    assignment: checked,
                  }))
                }
              />
            </div>
            <Divider />
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-slate-800">成绩异常预警</div>
                <div className="text-sm text-slate-400">
                  学生成绩大幅下降时通知
                </div>
              </div>
              <Switch
                checked={notifications.scoreAlert}
                onChange={(checked) =>
                  setNotifications((current) => ({
                    ...current,
                    scoreAlert: checked,
                  }))
                }
              />
            </div>
            <Divider />
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-slate-800">每日汇总</div>
                <div className="text-sm text-slate-400">
                  每天发送班级学习汇总
                </div>
              </div>
              <Switch
                checked={notifications.dailySummary}
                onChange={(checked) =>
                  setNotifications((current) => ({
                    ...current,
                    dailySummary: checked,
                  }))
                }
              />
            </div>
          </div>
        </Card>

        {/* 系统信息 */}
        <Card className="rounded-2xl border-0 shadow-sm" title="系统信息">
          <Spin spinning={loading}>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-slate-600">系统版本</span>
                <span className="font-medium">
                  v{systemInfo?.version || "-"}
                </span>
              </div>
              <Divider className="!my-3" />
              <div className="flex items-center justify-between">
                <span className="text-slate-600">AI模型</span>
                <Tag className="rounded-full border-0" color="blue">
                  {systemInfo?.ai_model || "-"}
                </Tag>
              </div>
              <Divider className="!my-3" />
              <div className="flex items-center justify-between">
                <span className="text-slate-600">数据库状态</span>
                <Tag
                  className="rounded-full border-0"
                  color={
                    systemInfo?.database_status === "normal"
                      ? "success"
                      : "error"
                  }
                >
                  {systemInfo?.database_status === "normal" ? "正常" : "异常"}
                </Tag>
              </div>
              <Divider className="!my-3" />
              <div className="flex items-center justify-between">
                <span className="text-slate-600">上次更新</span>
                <span className="text-slate-500">
                  {systemInfo?.last_updated
                    ? new Date(systemInfo.last_updated).toLocaleString(
                        "zh-CN",
                        {
                          year: "numeric",
                          month: "2-digit",
                          day: "2-digit",
                          hour: "2-digit",
                          minute: "2-digit",
                        },
                      )
                    : "-"}
                </span>
              </div>
            </div>
          </Spin>
        </Card>

        {/* 快捷操作 */}
        <Card className="rounded-2xl border-0 shadow-sm" title="快捷操作">
          <div className="space-y-3">
            <Button
              block
              className="text-left h-12 rounded-xl"
              onClick={clearCachedData}
            >
              <GlobalOutlined className="mr-2" />
              清除缓存
            </Button>
            <Button
              block
              className="text-left h-12 rounded-xl"
              onClick={resetNotifications}
            >
              <BellOutlined className="mr-2" />
              重置通知设置
            </Button>
            <Button
              block
              className="text-left h-12 rounded-xl"
              danger
              onClick={handleLogout}
            >
              <LockOutlined className="mr-2" />
              退出登录
            </Button>
          </div>
        </Card>
      </div>

      <div className="flex justify-end">
        <Button
          type="primary"
          icon={<SaveOutlined />}
          className="bg-[#0052ff] rounded-xl"
          loading={saving}
          onClick={saveNotifications}
        >
          保存设置
        </Button>
      </div>
    </div>
  );
};

export default SystemSettings;
