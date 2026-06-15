import React, { Suspense } from "react";
import { Spin } from "antd";
import { useAppStore } from "../store";
import CircuitSimulator from "./circuit-simulator/CircuitSimulator";

const ErrorDiagnosisC = React.lazy(() => import("./ErrorDiagnosisC"));

const ErrorDiagnosis: React.FC = () => {
  const currentSubject = useAppStore((s) => s.currentSubject);

  if (currentSubject === "电路分析") {
    return <CircuitSimulator />;
  }

  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center min-h-[60vh]">
          <Spin size="large" tip="加载中..." />
        </div>
      }
    >
      <ErrorDiagnosisC />
    </Suspense>
  );
};

export default ErrorDiagnosis;
