import React from "react";
import { Empty } from "antd";
import { LinkOutlined } from "@ant-design/icons";
import { useKBStore } from "../../store/kbStore";

interface BacklinksPanelProps {
  onNoteClick?: (noteId: string) => void;
}

const BacklinksPanel: React.FC<BacklinksPanelProps> = ({ onNoteClick }) => {
  const { backlinks, activeNoteId } = useKBStore();

  if (!activeNoteId) {
    return (
      <div className="h-full flex items-center justify-center text-slate-400">
        <div className="text-center">
          <LinkOutlined className="text-2xl mb-2" />
          <div className="text-xs">选择笔记查看反向链接</div>
        </div>
      </div>
    );
  }

  if (backlinks.length === 0) {
    return (
      <div className="h-full flex flex-col">
        <div className="px-3 py-2 border-b border-slate-200">
          <span className="text-sm font-medium text-slate-700">反向链接</span>
        </div>
        <Empty
          description="暂无反向链接"
          className="mt-8"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="px-3 py-2 border-b border-slate-200">
        <span className="text-sm font-medium text-slate-700">
          反向链接 ({backlinks.length})
        </span>
      </div>
      <div className="flex-1 overflow-auto">
        <div className="divide-y divide-slate-100">
          {backlinks.map((link) => (
            <div
              key={link.note_id}
              onClick={() => onNoteClick?.(link.note_id)}
              className="px-3 py-2 cursor-pointer hover:bg-slate-50 transition-colors"
            >
              <div className="text-sm font-medium text-indigo-600 hover:text-indigo-700">
                {link.title}
              </div>
              <div className="text-xs text-slate-400 mt-1 line-clamp-2">
                {link.excerpt}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default BacklinksPanel;
