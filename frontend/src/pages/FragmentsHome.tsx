/**
 * 白色碎片漂浮空间首页
 */
import React from "react";
import FragmentsSpace from "../components/holo/FragmentsSpace";
import { useHoloData } from "../components/holo/useHoloData";

const FragmentsHome: React.FC = () => {
  const { data } = useHoloData("student_001");
  return <FragmentsSpace data={data} />;
};

export default FragmentsHome;
