import * as Sentry from "@sentry/react";
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { ConfigProvider } from "antd";
import zhCN from "antd/locale/zh_CN";
import App from "./App";
import "./index.css";

Sentry.init({
  dsn: "替换为你的 Sentry DSN",
  integrations: [Sentry.browserTracingIntegration()],
  tracesSampleRate: 1.0,
});

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ConfigProvider locale={zhCN}>
      <BrowserRouter
        future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
      >
        <App />
      </BrowserRouter>
    </ConfigProvider>
  </React.StrictMode>,
);
