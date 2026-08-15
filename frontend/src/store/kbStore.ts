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
  searchResults: (KBNoteListItem & { score?: number; snippet?: string })[];
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
    set({ currentContent: content });
    const { activeNoteId } = get();
    if (activeNoteId) {
      get().updateNote(activeNoteId, { content });
    }
  },

  setTitle: (title: string) => {
    const { activeNoteId, activeNote } = get();
    if (activeNote) {
      set({ activeNote: { ...activeNote, title } });
    }
    if (activeNoteId) {
      get().updateNote(activeNoteId, { title });
    }
  },

  search: async (query: string) => {
    set({ searchQuery: query });
    if (!query.trim()) {
      set({ searchResults: [] });
      return;
    }
    try {
      // AIC RAG 升级：BM25 语义检索（相关度排序 + 命中片段）
      const res = await kbApi.ragSearch(query);
      const data = res.data?.data;
      if (res.data?.status === "success") {
        set({
          searchResults: Array.isArray(data) ? data : (data?.results ?? []),
        });
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
