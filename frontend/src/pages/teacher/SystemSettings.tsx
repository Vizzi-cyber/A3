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
import { teacherApi } from "../../services/api";

interface SystemInfo {
  version: string;
  ai_model: string;
  database_status: string;
  last_updated: string;
}

const SystemSettings: React.FC = () => {
  const userInfo = useAppStore((s) => s.userInfo);
  const [form] = Form.useForm();
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadSystemInfo();
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

  const handleSave = () => {
    form.validateFields().then(() => {
      message.success("设置已保存");
    });
  };

  return (
    <div className="space-y-6">
      <Typography.Title level={4} className="!m-0">
        系统设置
      </Typography.Title>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 账户信息 */}
        <Card className="rounded-2xl border-0 shadow-sm" title="账户信息">
          <Form form={form} layout="vertical">
            <Form.Item label="用户名">
              <Input
                prefix={<UserOutlined className="text-slate-400" />}
                defaultValue={userInfo?.username}
                disabled
              />
            </Form.Item>
            <Form.Item label="角色">
              <Tag className="rounded-full" color="blue">
                教师
              </Tag>
            </Form.Item>
            <Divider />
            <Form.Item label="修改密码">
              <Input.Password
                prefix={<LockOutlined className="text-slate-400" />}
                placeholder="当前密码"
                className="mb-3"
              />
              <Input.Password
                prefix={<LockOutlined className="text-slate-400" />}
                placeholder="新密码"
                className="mb-3"
              />
              <Input.Password
                prefix={<LockOutlined className="text-slate-400" />}
                placeholder="确认新密码"
              />
            </Form.Item>
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
              <Switch defaultChecked />
            </div>
            <Divider />
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-slate-800">作业提交通知</div>
                <div className="text-sm text-slate-400">学生提交作业时通知</div>
              </div>
              <Switch defaultChecked />
            </div>
            <Divider />
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-slate-800">成绩异常预警</div>
                <div className="text-sm text-slate-400">
                  学生成绩大幅下降时通知
                </div>
              </div>
              <Switch defaultChecked />
            </div>
            <Divider />
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-slate-800">每日汇总</div>
                <div className="text-sm text-slate-400">
                  每天发送班级学习汇总
                </div>
              </div>
              <Switch />
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
            <Button block className="text-left h-12 rounded-xl">
              <GlobalOutlined className="mr-2" />
              清除缓存
            </Button>
            <Button block className="text-left h-12 rounded-xl">
              <BellOutlined className="mr-2" />
              重置通知设置
            </Button>
            <Button block className="text-left h-12 rounded-xl" danger>
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
        >
          保存设置
        </Button>
      </div>
    </div>
  );
};

export default SystemSettings;
