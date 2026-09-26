import React from "react";
import { Button, Result } from "antd";
import { useNavigate } from "react-router-dom";
import { HomeOutlined } from "@ant-design/icons";

const NotFound: React.FC = () => {
  const navigate = useNavigate();
  return (
    <div className="relative flex min-h-[70vh] items-center justify-center overflow-hidden px-6 py-12">
      <div className="pointer-events-none absolute -top-16 right-0 h-72 w-72 rounded-full bg-indigo-100/60 blur-3xl" />
      <div className="pointer-events-none absolute bottom-0 -left-12 h-64 w-64 rounded-full bg-sky-100/50 blur-3xl" />
      <div className="relative z-10 w-full max-w-xl overflow-hidden rounded-2xl border border-slate-100 bg-white shadow-card">
        <div className="pointer-events-none absolute -right-20 -top-20 h-48 w-48 rounded-full bg-violet-100/45 blur-3xl" />
        <Result
          status="404"
          title={
            <span className="font-bold tracking-tight text-slate-800">404</span>
          }
          subTitle={
            <span className="text-slate-500">抱歉，你访问的页面不存在</span>
          }
          extra={
            <Button
              type="primary"
              size="large"
              icon={<HomeOutlined />}
              onClick={() => navigate("/")}
              className="rounded-full border-0 bg-primary px-6 shadow-glow"
            >
              返回首页
            </Button>
          }
        />
      </div>
    </div>
  );
};

export default NotFound;
