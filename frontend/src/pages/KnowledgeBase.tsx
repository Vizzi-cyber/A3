import React, { useEffect, useState } from "react";
import { Tabs, Spin } from "antd";
import {
  FolderOutlined,
  SearchOutlined,
  ApartmentOutlined,
  LinkOutlined,
} from "@ant-design/icons";
import { useKBStore } from "../store/kbStore";
import FileTree from "../components/kb/FileTree";
import NoteList from "../components/kb/NoteList";
import NoteEditor from "../components/kb/NoteEditor";
import BacklinksPanel from "../components/kb/BacklinksPanel";
import SearchPanel from "../components/kb/SearchPanel";
import KnowledgeGraph from "../components/kb/KnowledgeGraph";

const KnowledgeBase: React.FC = () => {
  const { loadFolders, loadNotes, selectNote, activeNoteId } = useKBStore();
  const [loading, setLoading] = useState(true);
  const [rightTab, setRightTab] = useState("backlinks");

  useEffect(() => {
    const init = async () => {
      try {
        await Promise.all([loadFolders(), loadNotes()]);
      } catch {
        // ignore load errors, show empty state
      } finally {
        setLoading(false);
      }
    };
    init();
  }, []);

  const handleNoteSelect = (noteId: string) => {
    selectNote(noteId);
  };

  if (loading) {
    return (
      <div
        className="flex items-center justify-center"
        style={{ height: "calc(100vh - 128px)" }}
      >
        <Spin size="large" tip="加载知识库...">
          <div style={{ padding: 50 }} />
        </Spin>
      </div>
    );
  }

  return (
    <div
      className="flex bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden"
      style={{ height: "calc(100vh - 128px)" }}
    >
      {/* 左侧面板：文件夹树 + 搜索 */}
      <div className="w-56 border-r border-slate-200 flex flex-col shrink-0">
        <Tabs
          defaultActiveKey="folders"
          className="h-full flex flex-col"
          tabBarStyle={{ paddingLeft: 8, marginBottom: 0, fontSize: 12 }}
          items={[
            {
              key: "folders",
              label: (
                <span className="text-xs">
                  <FolderOutlined /> 文件夹
                </span>
              ),
              children: (
                <div
                  className="overflow-hidden"
                  style={{ height: "calc(100% - 44px)" }}
                >
                  <FileTree onNoteSelect={handleNoteSelect} />
                </div>
              ),
            },
            {
              key: "search",
              label: (
                <span className="text-xs">
                  <SearchOutlined /> 搜索
                </span>
              ),
              children: (
                <div
                  className="overflow-hidden"
                  style={{ height: "calc(100% - 44px)" }}
                >
                  <SearchPanel onNoteClick={handleNoteSelect} />
                </div>
              ),
            },
          ]}
        />
      </div>

      {/* 中间面板：笔记列表 + 编辑器 */}
      <div className="flex-1 flex min-w-0">
        {/* 笔记列表 */}
        <div className="w-52 border-r border-slate-200 shrink-0 bg-white">
          <NoteList onNoteSelect={handleNoteSelect} />
        </div>

        {/* 编辑器 */}
        <div className="flex-1 min-w-0">
          <NoteEditor />
        </div>
      </div>

      {/* 右侧面板：反向链接 + 知识图谱 */}
      {activeNoteId && (
        <div className="w-64 border-l border-slate-200 flex flex-col shrink-0">
          <Tabs
            activeKey={rightTab}
            onChange={setRightTab}
            className="h-full"
            tabBarStyle={{ paddingLeft: 8, marginBottom: 0, fontSize: 12 }}
            items={[
              {
                key: "backlinks",
                label: (
                  <span className="text-xs">
                    <LinkOutlined /> 反向链接
                  </span>
                ),
                children: (
                  <div
                    className="overflow-hidden"
                    style={{ height: "calc(100vh - 220px)" }}
                  >
                    <BacklinksPanel onNoteClick={handleNoteSelect} />
                  </div>
                ),
              },
              {
                key: "graph",
                label: (
                  <span className="text-xs">
                    <ApartmentOutlined /> 图谱
                  </span>
                ),
                children: (
                  <div
                    className="overflow-hidden"
                    style={{ height: "calc(100vh - 220px)" }}
                  >
                    <KnowledgeGraph onNoteClick={handleNoteSelect} />
                  </div>
                ),
              },
            ]}
          />
        </div>
      )}
    </div>
  );
};

export default KnowledgeBase;
