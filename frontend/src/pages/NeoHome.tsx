/**
 * 知识空间首页（3D 数据指挥舱总览 + 悬浮工具条）
 * 顶部固定元素已移除；日历/每日练习/今日任务/排行榜收为右上角悬浮按钮。
 */
import React from "react";
import NeoConsole from "../components/holo/NeoConsole";
import FloatingTools from "../components/holo/FloatingTools";
import AlgorithmStatusBar from "../components/holo/AlgorithmStatusBar";
import { useHoloData } from "../components/holo/useHoloData";

const NeoHome: React.FC = () => {
  const { data } = useHoloData("student_001");
  return (
    <div className="relative">
      <NeoConsole data={data} />
      <FloatingTools data={data} />
      {/* AI 引擎状态条（左下角） */}
      <div className="fixed bottom-4 left-4" style={{ zIndex: 9000 }}>
        <AlgorithmStatusBar />
      </div>
    </div>
  );
};

export default NeoHome;
