import React from "react";
import { Card, Table, Button, Tag, Space, Typography } from "antd";
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
} from "@ant-design/icons";

const AssignmentManagement: React.FC = () => {
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

  const data = [
    {
      key: "1",
      name: "指针基础练习",
      knowledge_point: "指针概念",
      deadline: "2024-01-20",
      submitted: 15,
      total: 20,
      status: "active",
    },
    {
      key: "2",
      name: "数组排序实验",
      knowledge_point: "数组与排序",
      deadline: "2024-01-18",
      submitted: 20,
      total: 20,
      status: "completed",
    },
    {
      key: "3",
      name: "文件操作综合题",
      knowledge_point: "文件I/O",
      deadline: "2024-01-25",
      submitted: 0,
      total: 20,
      status: "draft",
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
        <Table columns={columns} dataSource={data} pagination={false} />
      </Card>
    </div>
  );
};

export default AssignmentManagement;
