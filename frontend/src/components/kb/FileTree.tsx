import React, { useState } from "react";
import { Tree, Dropdown, Modal, Input, message } from "antd";
import {
  FolderOutlined,
  FolderOpenOutlined,
  FileTextOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  FolderAddOutlined,
} from "@ant-design/icons";
import type { DataNode } from "antd/es/tree";
import { useKBStore } from "../../store/kbStore";

interface FileTreeProps {
  onNoteSelect?: (noteId: string) => void;
}

const FileTree: React.FC<FileTreeProps> = ({ onNoteSelect }) => {
  const {
    folders,
    notes,
    currentFolderId,
    loadNotes,
    createFolder,
    deleteFolder,
    renameFolder,
    createNote,
  } = useKBStore();
  const [modalVisible, setModalVisible] = useState(false);
  const [modalType, setModalType] = useState<"folder" | "note">("folder");
  const [editingFolderId, setEditingFolderId] = useState<string | null>(null);
  const [inputValue, setInputValue] = useState("");
  const [contextMenuFolderId, setContextMenuFolderId] = useState<string | null>(
    null,
  );

  const buildTreeData = (): DataNode[] => {
    const rootFolders = folders.filter((f) => !f.parent_id);
    const childMap = new Map<string, typeof folders>();
    folders.forEach((f) => {
      if (f.parent_id) {
        const children = childMap.get(f.parent_id) || [];
        children.push(f);
        childMap.set(f.parent_id, children);
      }
    });

    const buildFolderNode = (folder: (typeof folders)[0]): DataNode => {
      const children = childMap.get(folder.folder_id) || [];
      const folderNotes = notes.filter((n) => n.folder_id === folder.folder_id);
      return {
        key: `folder-${folder.folder_id}`,
        title: folder.name,
        icon:
          currentFolderId === folder.folder_id ? (
            <FolderOpenOutlined />
          ) : (
            <FolderOutlined />
          ),
        children: [
          ...children.map((c) => buildFolderNode(c)),
          ...folderNotes.map((n) => ({
            key: `note-${n.note_id}`,
            title: n.title,
            icon: <FileTextOutlined />,
            isLeaf: true,
          })),
        ],
      };
    };

    const rootNotes = notes.filter((n) => !n.folder_id);
    return [
      ...rootFolders.map((f) => buildFolderNode(f)),
      ...rootNotes.map((n) => ({
        key: `note-${n.note_id}`,
        title: n.title,
        icon: <FileTextOutlined />,
        isLeaf: true,
      })),
    ];
  };

  const handleSelect = (selectedKeys: React.Key[]) => {
    const key = selectedKeys[0] as string;
    if (key?.startsWith("note-")) {
      const noteId = key.replace("note-", "");
      onNoteSelect?.(noteId);
    } else if (key?.startsWith("folder-")) {
      const folderId = key.replace("folder-", "");
      loadNotes(folderId);
    }
  };

  const handleContextMenu = (info: { node: any; event: React.MouseEvent }) => {
    const key = info.node.key as string;
    if (key?.startsWith("folder-")) {
      const folderId = key.replace("folder-", "");
      setContextMenuFolderId(folderId);
    }
  };

  const handleCreateFolder = async () => {
    if (!inputValue.trim()) return;
    if (editingFolderId) {
      await renameFolder(editingFolderId, inputValue.trim());
      message.success("文件夹已重命名");
    } else {
      await createFolder(inputValue.trim(), contextMenuFolderId);
      message.success("文件夹已创建");
    }
    setModalVisible(false);
    setInputValue("");
    setEditingFolderId(null);
    setContextMenuFolderId(null);
  };

  const handleCreateNote = async () => {
    if (!inputValue.trim()) return;
    await createNote(inputValue.trim(), contextMenuFolderId);
    message.success("笔记已创建");
    setModalVisible(false);
    setInputValue("");
    setContextMenuFolderId(null);
  };

  const showCreateFolderModal = (parentId?: string) => {
    setContextMenuFolderId(parentId || null);
    setEditingFolderId(null);
    setModalType("folder");
    setInputValue("");
    setModalVisible(true);
  };

  const showRenameFolderModal = (folderId: string) => {
    const folder = folders.find((f) => f.folder_id === folderId);
    setEditingFolderId(folderId);
    setModalType("folder");
    setInputValue(folder?.name || "");
    setModalVisible(true);
  };

  const handleDeleteFolder = async (folderId: string) => {
    Modal.confirm({
      title: "确认删除",
      content: "删除文件夹将同时删除其下的所有笔记，确认继续？",
      onOk: async () => {
        await deleteFolder(folderId);
        message.success("文件夹已删除");
      },
    });
  };

  const handleRightClick = ({ node }: any) => {
    const key = node.key as string;
    if (key?.startsWith("folder-")) {
      const folderId = key.replace("folder-", "");
      return {
        items: [
          {
            key: "new-note",
            icon: <PlusOutlined />,
            label: "新建笔记",
            onClick: () => {
              setContextMenuFolderId(folderId);
              setModalType("note");
              setInputValue("");
              setModalVisible(true);
            },
          },
          {
            key: "new-subfolder",
            icon: <FolderAddOutlined />,
            label: "新建子文件夹",
            onClick: () => showCreateFolderModal(folderId),
          },
          {
            key: "rename",
            icon: <EditOutlined />,
            label: "重命名",
            onClick: () => showRenameFolderModal(folderId),
          },
          {
            key: "delete",
            icon: <DeleteOutlined />,
            label: "删除",
            danger: true,
            onClick: () => handleDeleteFolder(folderId),
          },
        ],
      };
    }
    return undefined;
  };

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between px-3 py-2 border-b border-slate-200">
        <span className="text-sm font-medium text-slate-700">文件夹</span>
        <div className="flex gap-1">
          <button
            onClick={() => showCreateFolderModal()}
            className="p-1 rounded hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
            title="新建文件夹"
          >
            <FolderAddOutlined />
          </button>
          <button
            onClick={() => {
              setContextMenuFolderId(null);
              setModalType("note");
              setInputValue("");
              setModalVisible(true);
            }}
            className="p-1 rounded hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
            title="新建笔记"
          >
            <PlusOutlined />
          </button>
        </div>
      </div>
      <div className="flex-1 overflow-auto p-1">
        <Tree
          treeData={buildTreeData()}
          onSelect={handleSelect}
          onRightClick={handleRightClick}
          showIcon
          blockNode
          defaultExpandAll
        />
      </div>

      <Modal
        title={
          modalType === "folder"
            ? editingFolderId
              ? "重命名文件夹"
              : "新建文件夹"
            : "新建笔记"
        }
        open={modalVisible}
        onOk={modalType === "folder" ? handleCreateFolder : handleCreateNote}
        onCancel={() => {
          setModalVisible(false);
          setInputValue("");
          setEditingFolderId(null);
        }}
        okText="确认"
        cancelText="取消"
      >
        <Input
          placeholder={
            modalType === "folder" ? "输入文件夹名称" : "输入笔记标题"
          }
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onPressEnter={
            modalType === "folder" ? handleCreateFolder : handleCreateNote
          }
          autoFocus
        />
      </Modal>
    </div>
  );
};

export default FileTree;
