import React from "react";
import { Card, Table, Button, Tag, Space, Typography, Empty } from "antd";
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
} from "@ant-design/icons";
import { useAppStore } from "../../store";

interface Assignment {
  key: string;
  name: string;
  knowledge_point: string;
  deadline: string;
  submitted: number;
  total: number;
  status: string;
}

const AssignmentManagement: React.FC = () => {
  const userInfo = useAppStore((s) => s.userInfo);

  // 后端暂无作业管理API，显示空状态
  const assignments: Assignment[] = [];

  const columns = [
    {
      title: "作业名称",
      dataIndex: "name",
      key: "name",
      render: (name: string) => <span className="font-medium">{name}</span>,
    },
    {
      title: "关联知识点",
      dataIndex: "knowledge_point",
      key: "knowledge_point",
    },
    {
      title: "截止时间",
      dataIndex: "deadline",
      key: "deadline",
    },
    {
      title: "提交人数",
      dataIndex: "submitted",
      key: "submitted",
      render: (text: string, record: { total: number }) =>
        `${text}/${record.total}`,
    },
    {
      title: "状态",
      dataIndex: "status",
      key: "status",
      render: (status: string) => (
        <Tag
          className="rounded-full border-0"
          color={
            status === "active"
              ? "success"
              : status === "draft"
                ? "default"
                : "warning"
          }
        >
          {status === "active"
            ? "进行中"
            : status === "draft"
              ? "草稿"
              : "已截止"}
        </Tag>
      ),
    },
    {
      title: "操作",
      key: "action",
      render: () => (
        <Space>
          <Button type="link" size="small" icon={<EyeOutlined />}>
            查看
          </Button>
          <Button type="link" size="small" icon={<EditOutlined />}>
            编辑
          </Button>
          <Button type="link" size="small" danger icon={<DeleteOutlined />}>
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Typography.Title level={4} className="!m-0">
          作业管理
        </Typography.Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          className="bg-[#0052ff] rounded-xl"
        >
          创建作业
        </Button>
      </div>

      <Card className="rounded-2xl border-0 shadow-sm">
        <Table
          columns={columns}
          dataSource={assignments}
          loading={false}
          pagination={false}
          locale={{
            emptyText: <Empty description="暂无作业数据，请创建作业" />,
          }}
        />
      </Card>
    </div>
  );
};

export default AssignmentManagement;
