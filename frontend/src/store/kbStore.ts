import { create } from "zustand";
import { message } from "antd";
import { kbApi } from "../services/knowledgeBaseApi";
import type {
  KBFolder,
  KBNoteListItem,
  KBNote,
  BacklinkItem,
} from "../types/knowledgeBase";

interface KBState {
  folders: KBFolder[];
  notes: KBNoteListItem[];
  activeNoteId: string | null;
  activeNote: KBNote | null;
  currentFolderId: string | null;
  searchQuery: string;
  searchResults: KBNoteListItem[];
  backlinks: BacklinkItem[];
  isDirty: boolean;
  currentContent: string;
  loading: boolean;

  loadFolders: () => Promise<void>;
  loadNotes: (folderId?: string | null) => Promise<void>;
  selectNote: (noteId: string) => Promise<void>;
  createNote: (
    title: string,
    folderId?: string | null,
  ) => Promise<string | null>;
  updateNote: (
    noteId: string,
    data: { title?: string; content?: string },
  ) => Promise<void>;
  deleteNote: (noteId: string) => Promise<void>;
  setContent: (content: string) => void;
  setTitle: (title: string) => void;
  search: (query: string) => Promise<void>;
  loadBacklinks: (noteId: string) => Promise<void>;
  createFolder: (name: string, parentId?: string | null) => Promise<void>;
  deleteFolder: (folderId: string) => Promise<void>;
  renameFolder: (folderId: string, name: string) => Promise<void>;
}

const AUTOSAVE_DEBOUNCE_MS = 500;

// 模块级防抖状态：setContent/setTitle 任一变更都重置同一个窗口，
// 最终把标题+内容合并为一次 PATCH（zustand store 只初始化一次，模块级变量安全）
let saveTimer: ReturnType<typeof setTimeout> | null = null;
let pendingSave: {
  noteId: string;
  data: { title?: string; content?: string };
} | null = null;

/** 立即落盘未触发的防抖保存（切换/删除笔记前调用，防丢尾字） */
function flushPendingSave() {
  if (saveTimer) {
    clearTimeout(saveTimer);
    saveTimer = null;
  }
  if (pendingSave) {
    const { noteId, data } = pendingSave;
    pendingSave = null;
    void useKBStore.getState().updateNote(noteId, data);
  }
}

function scheduleAutosave() {
  const { activeNoteId, activeNote } = useKBStore.getState();
  if (!activeNoteId || !activeNote) return;
  pendingSave = {
    noteId: activeNoteId,
    data: {
      title: activeNote.title,
      content: useKBStore.getState().currentContent,
    },
  };
  useKBStore.setState({ isDirty: true });
  if (saveTimer) clearTimeout(saveTimer);
  saveTimer = setTimeout(() => {
    saveTimer = null;
    flushPendingSave();
  }, AUTOSAVE_DEBOUNCE_MS);
}

export const useKBStore = create<KBState>((set, get) => ({
  folders: [],
  notes: [],
  activeNoteId: null,
  activeNote: null,
  currentFolderId: null,
  searchQuery: "",
  searchResults: [],
  backlinks: [],
  isDirty: false,
  currentContent: "",
  loading: false,

  loadFolders: async () => {
    try {
      const res = await kbApi.listFolders();
      if (res.data?.status === "success") {
        set({ folders: res.data.data });
      }
    } catch {
      message.error("加载文件夹失败");
    }
  },

  loadNotes: async (folderId?: string | null) => {
    set({ loading: true, currentFolderId: folderId ?? null });
    try {
      const res = await kbApi.listNotes(folderId ?? undefined);
      if (res.data?.status === "success") {
        set({ notes: res.data.data });
      }
    } catch {
      message.error("加载笔记列表失败");
    }
    set({ loading: false });
  },

  selectNote: async (noteId: string) => {
    try {
      // 切换前先把上一篇未落盘的编辑立即保存，防止防抖窗口内的尾字丢失
      flushPendingSave();
      const res = await kbApi.getNote(noteId);
      if (res.data?.status === "success") {
        const note = res.data.data;
        set({
          activeNoteId: noteId,
          activeNote: note,
          currentContent: note.content,
          isDirty: false,
        });
        get().loadBacklinks(noteId);
      }
    } catch {
      message.error("加载笔记内容失败");
    }
  },

  createNote: async (title: string, folderId?: string | null) => {
    try {
      const res = await kbApi.createNote({
        title,
        content: "",
        folder_id: folderId ?? undefined,
      });
      if (res.data?.status === "success") {
        const note = res.data.data;
        set((s) => ({
          notes: [
            {
              note_id: note.note_id,
              title: note.title,
              content_preview: "",
              folder_id: note.folder_id,
              updated_at: note.updated_at,
            },
            ...s.notes,
          ],
        }));
        await get().selectNote(note.note_id);
        return note.note_id;
      }
    } catch {
      message.error("创建笔记失败");
    }
    return null;
  },

  updateNote: async (
    noteId: string,
    data: { title?: string; content?: string },
  ) => {
    try {
      await kbApi.updateNote(noteId, data);
      set((s) => ({
        notes: s.notes.map((n) =>
          n.note_id === noteId
            ? {
                ...n,
                title: data.title ?? n.title,
                content_preview: (data.content ?? "").slice(0, 200),
              }
            : n,
        ),
        isDirty: false,
      }));
    } catch {
      message.error("保存笔记失败");
    }
  },

  deleteNote: async (noteId: string) => {
    try {
      // 若删除的正是当前笔记，先把未落盘的编辑冲刷掉再删，避免对已删笔记发起保存
      if (get().activeNoteId === noteId) {
        flushPendingSave();
      }
      await kbApi.deleteNote(noteId);
      set((s) => ({
        notes: s.notes.filter((n) => n.note_id !== noteId),
        activeNoteId: s.activeNoteId === noteId ? null : s.activeNoteId,
        activeNote: s.activeNoteId === noteId ? null : s.activeNote,
        currentContent: s.activeNoteId === noteId ? "" : s.currentContent,
      }));
    } catch {
      message.error("删除笔记失败");
    }
  },

  setContent: (content: string) => {
    // 本地状态立即更新（Monaco 受控组件 + 分屏预览实时刷新），保存走 500ms 防抖
    set({ currentContent: content });
    scheduleAutosave();
  },

  setTitle: (title: string) => {
    const { activeNote } = get();
    if (activeNote) {
      set({ activeNote: { ...activeNote, title } });
    }
    scheduleAutosave();
  },

  search: async (query: string) => {
    set({ searchQuery: query });
    if (!query.trim()) {
      set({ searchResults: [] });
      return;
    }
    try {
      const res = await kbApi.searchNotes(query);
      if (res.data?.status === "success") {
        set({ searchResults: res.data.data });
      }
    } catch {
      message.error("搜索笔记失败");
    }
  },

  loadBacklinks: async (noteId: string) => {
    try {
      const res = await kbApi.getBacklinks(noteId);
      if (res.data?.status === "success") {
        set({ backlinks: res.data.data });
      }
    } catch {
      message.error("加载反向链接失败");
    }
  },

  createFolder: async (name: string, parentId?: string | null) => {
    try {
      const res = await kbApi.createFolder({
        name,
        parent_id: parentId ?? undefined,
      });
      if (res.data?.status === "success") {
        set((s) => ({ folders: [...s.folders, res.data.data] }));
      }
    } catch {
      message.error("创建文件夹失败");
    }
  },

  deleteFolder: async (folderId: string) => {
    try {
      await kbApi.deleteFolder(folderId);
      set((s) => ({
        folders: s.folders.filter((f) => f.folder_id !== folderId),
      }));
      get().loadNotes(null);
    } catch {
      message.error("删除文件夹失败");
    }
  },

  renameFolder: async (folderId: string, name: string) => {
    try {
      await kbApi.renameFolder(folderId, name);
      set((s) => ({
        folders: s.folders.map((f) =>
          f.folder_id === folderId ? { ...f, name } : f,
        ),
      }));
    } catch {
      message.error("重命名文件夹失败");
    }
  },
}));
