import React, { useState, useCallback, useEffect } from "react";
import { Spin } from "antd";
import {
  EditOutlined,
  EyeOutlined,
  SplitCellsOutlined,
} from "@ant-design/icons";
import Editor from "@monaco-editor/react";
import { useKBStore } from "../../store/kbStore";
import WikiLinkMarkdown from "./WikiLinkMarkdown";

type ViewMode = "editor" | "split" | "preview";

const NoteEditor: React.FC = () => {
  const {
    activeNote,
    activeNoteId,
    currentContent,
    isDirty,
    setContent,
    setTitle,
    notes,
  } = useKBStore();
  const [viewMode, setViewMode] = useState<ViewMode>("preview");
  const [titleValue, setTitleValue] = useState("");

  useEffect(() => {
    if (activeNote) {
      setTitleValue(activeNote.title);
    }
  }, [activeNote]);

  const handleContentChange = useCallback(
    (value: string | undefined) => {
      if (value !== undefined) {
        setContent(value);
      }
    },
    [setContent],
  );

  const handleTitleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = e.target.value;
      setTitleValue(value);
      setTitle(value);
    },
    [setTitle],
  );

  if (!activeNote) {
    return (
      <div className="h-full flex items-center justify-center bg-white">
        <div className="text-center text-slate-400">
          <EditOutlined className="text-4xl mb-3" />
          <div className="text-sm">选择或创建一篇笔记开始编辑</div>
        </div>
      </div>
    );
  }

  const modes: { key: ViewMode; icon: React.ReactNode; label: string }[] = [
    { key: "editor", icon: <EditOutlined />, label: "编辑" },
    { key: "split", icon: <SplitCellsOutlined />, label: "分屏" },
    { key: "preview", icon: <EyeOutlined />, label: "预览" },
  ];

  return (
    <div className="h-full flex flex-col bg-white">
      {/* 标题栏 */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-slate-200 shrink-0">
        <div className="flex items-center min-w-0 flex-1">
          <input
            type="text"
            value={titleValue}
            onChange={handleTitleChange}
            className="flex-1 text-lg font-bold text-slate-800 outline-none border-none bg-transparent placeholder-slate-300"
            placeholder="笔记标题"
          />
          {isDirty && <span className="ml-2 text-amber-500 text-xs">●</span>}
        </div>
        <div className="flex items-center gap-0.5 ml-2">
          {modes.map(({ key, icon, label }) => (
            <button
              key={key}
              onClick={() => setViewMode(key)}
              title={label}
              className={`p-1.5 rounded text-xs transition-colors ${
                viewMode === key
                  ? "bg-indigo-100 text-indigo-600"
                  : "text-slate-400 hover:text-slate-600"
              }`}
            >
              {icon}
            </button>
          ))}
        </div>
      </div>

      {/* 编辑器区域 */}
      <div className="flex-1 min-h-0 overflow-hidden">
        {viewMode === "split" ? (
          <div className="h-full flex">
            <div className="w-1/2 border-r border-slate-200">
              <Editor
                height="100%"
                language="markdown"
                value={currentContent}
                onChange={handleContentChange}
                theme="vs-dark"
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: "on",
                  wordWrap: "on",
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                  padding: { top: 12 },
                }}
              />
            </div>
            <div className="w-1/2 overflow-auto p-6">
              <WikiLinkMarkdown content={currentContent} notes={notes} />
            </div>
          </div>
        ) : viewMode === "editor" ? (
          <Editor
            height="100%"
            language="markdown"
            value={currentContent}
            onChange={handleContentChange}
            theme="vs-dark"
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              lineNumbers: "on",
              wordWrap: "on",
              scrollBeyondLastLine: false,
              automaticLayout: true,
              padding: { top: 12 },
            }}
          />
        ) : (
          <div className="h-full overflow-auto p-6">
            <WikiLinkMarkdown content={currentContent} notes={notes} />
          </div>
        )}
      </div>
    </div>
  );
};

export default NoteEditor;
