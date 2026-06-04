import React from "react";
import { Button, Empty, Spin } from "antd";
import { PlusOutlined, FileTextOutlined } from "@ant-design/icons";
import { useKBStore } from "../../store/kbStore";

interface NoteListProps {
  onNoteSelect?: (noteId: string) => void;
}

const NoteList: React.FC<NoteListProps> = ({ onNoteSelect }) => {
  const {
    notes,
    activeNoteId,
    loading,
    createNote,
    loadNotes,
    currentFolderId,
  } = useKBStore();

  const handleCreateNote = async () => {
    const noteId = await createNote("未命名笔记", currentFolderId);
    if (noteId) {
      onNoteSelect?.(noteId);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-32">
        <Spin size="small" />
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between px-3 py-2 border-b border-slate-200">
        <span className="text-sm font-medium text-slate-700">
          笔记 ({notes.length})
        </span>
        <Button
          type="primary"
          size="small"
          icon={<PlusOutlined />}
          onClick={handleCreateNote}
        >
          新建
        </Button>
      </div>
      <div className="flex-1 overflow-auto">
        {notes.length === 0 ? (
          <Empty
            description="暂无笔记"
            className="mt-8"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        ) : (
          <div className="divide-y divide-slate-100">
            {notes.map((note) => (
              <div
                key={note.note_id}
                onClick={() => onNoteSelect?.(note.note_id)}
                className={`px-3 py-3 cursor-pointer transition-colors ${
                  activeNoteId === note.note_id
                    ? "bg-indigo-50 border-l-2 border-indigo-500"
                    : "hover:bg-slate-50 border-l-2 border-transparent"
                }`}
              >
                <div className="flex items-start gap-2">
                  <FileTextOutlined className="text-slate-400 mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-slate-700 truncate">
                      {note.title}
                    </div>
                    <div className="text-xs text-slate-400 mt-1 line-clamp-2">
                      {note.content_preview || "暂无内容"}
                    </div>
                    <div className="text-xs text-slate-300 mt-1">
                      {note.updated_at
                        ? new Date(note.updated_at).toLocaleString("zh-CN")
                        : ""}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default NoteList;
