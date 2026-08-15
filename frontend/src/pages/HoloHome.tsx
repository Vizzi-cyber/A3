/**
 * 全息学习空间首页
 */
import React from "react";
import HoloSpace from "../components/holo/HoloSpace";
import { useHoloData } from "../components/holo/useHoloData";

const HoloHome: React.FC = () => {
  const { data, loaded } = useHoloData("student_001");
  return <HoloSpace data={data} />;
};

export default HoloHome;
