import React, { useState, useCallback, useEffect } from "react";
import { Input, Empty, Spin } from "antd";
import { SearchOutlined, FileTextOutlined } from "@ant-design/icons";
import { useKBStore } from "../../store/kbStore";

interface SearchPanelProps {
  onNoteClick?: (noteId: string) => void;
}

const SearchPanel: React.FC<SearchPanelProps> = ({ onNoteClick }) => {
  const { searchQuery, searchResults, search } = useKBStore();
  const [inputValue, setInputValue] = useState(searchQuery);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setInputValue(searchQuery);
  }, [searchQuery]);

  const handleSearch = useCallback(
    async (value: string) => {
      setLoading(true);
      await search(value);
      setLoading(false);
    },
    [search],
  );

  useEffect(() => {
    const timer = setTimeout(() => {
      handleSearch(inputValue);
    }, 300);
    return () => clearTimeout(timer);
  }, [inputValue, handleSearch]);

  return (
    <div className="h-full flex flex-col">
      <div className="px-3 py-2 border-b border-slate-200">
        <Input
          prefix={<SearchOutlined className="text-slate-400" />}
          placeholder="搜索笔记..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          allowClear
          size="small"
        />
      </div>
      <div className="flex-1 overflow-auto">
        {loading ? (
          <div className="flex items-center justify-center h-32">
            <Spin size="small" />
          </div>
        ) : searchResults.length === 0 ? (
          <Empty
            description={inputValue ? "未找到匹配结果" : "输入关键词搜索"}
            className="mt-8"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        ) : (
          <div className="divide-y divide-slate-100">
            {searchResults.map((note) => (
              <div
                key={note.note_id}
                onClick={() => onNoteClick?.(note.note_id)}
                className="px-3 py-2 cursor-pointer hover:bg-slate-50 transition-colors"
              >
                <div className="flex items-center gap-2">
                  <FileTextOutlined className="text-slate-400" />
                  <div className="text-sm font-medium text-slate-700 truncate flex-1">
                    {note.title}
                  </div>
                  {note.score != null && (
                    <span
                      className="text-[10px] px-1.5 py-0.5 rounded-full shrink-0"
                      style={{
                        background: (note.score ?? 0) > 2 ? "#ecfdf5" : "#eef2ff",
                        color: (note.score ?? 0) > 2 ? "#059669" : "#6366f1",
                      }}
                    >
                      {(Math.min((note.score ?? 0) / 3, 1) * 100).toFixed(0)}% 相关
                    </span>
                  )}
                </div>
                <div className="text-xs text-slate-400 mt-1 line-clamp-2 ml-5">
                  {note.snippet ?? note.content_preview}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchPanel;
