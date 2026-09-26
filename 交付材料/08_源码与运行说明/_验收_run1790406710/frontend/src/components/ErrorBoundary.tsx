import React, { Component, ErrorInfo, ReactNode } from "react";
import { Button, Result } from "antd";
import { useNavigate } from "react-router-dom";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/** 类组件无法使用 hooks，用包装组件注入 navigate */
function withNavigate(WrappedComponent: React.ComponentClass<InnerProps>) {
  return function ErrorBoundaryWithNavigate(props: Props) {
    const navigate = useNavigate();
    return <WrappedComponent {...props} navigate={navigate} />;
  };
}

interface InnerProps extends Props {
  navigate?: (_to: string) => void;
}

class ErrorBoundaryInner extends Component<InnerProps, State> {
  constructor(props: InnerProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("ErrorBoundary caught:", error, errorInfo);
    try {
      import("@sentry/react").then((Sentry) => {
        Sentry.captureException(error, {
          extra: { componentStack: errorInfo.componentStack },
        });
      });
    } catch {}
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  handleGoHome = () => {
    if (this.props.navigate) {
      this.props.navigate("/");
    } else {
      window.location.href = "/";
    }
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return (
        <div className="flex items-center justify-center min-h-[60vh]">
          <Result
            status="error"
            title="页面加载失败"
            subTitle={this.state.error?.message || "发生了未知错误"}
            extra={[
              <Button key="retry" type="primary" onClick={this.handleReset}>
                重试
              </Button>,
              <Button key="home" onClick={this.handleGoHome}>
                返回首页
              </Button>,
            ]}
          />
        </div>
      );
    }

    return this.props.children;
  }
}

export const ErrorBoundary = withNavigate(ErrorBoundaryInner);
