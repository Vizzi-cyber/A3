import { api } from "./api";
import type {
  KBFolder,
  KBNote,
  KBNoteListItem,
  BacklinkItem,
  GraphNode,
  GraphEdge,
} from "../types/knowledgeBase";

export const kbApi = {
  // Folders
  listFolders: () =>
    api.get<{ status: string; data: KBFolder[] }>("/kb/folders"),
  createFolder: (data: { name: string; parent_id?: string }) =>
    api.post<{ status: string; data: KBFolder }>("/kb/folders", data),
  renameFolder: (folderId: string, name: string) =>
    api.put<{ status: string }>(`/kb/folders/${folderId}`, { name }),
  deleteFolder: (folderId: string) =>
    api.delete<{ status: string }>(`/kb/folders/${folderId}`),

  // Notes
  listNotes: (folderId?: string) =>
    api.get<{ status: string; data: KBNoteListItem[] }>("/kb/notes", {
      params: folderId ? { folder_id: folderId } : undefined,
    }),
  getNote: (noteId: string) =>
    api.get<{ status: string; data: KBNote }>(`/kb/notes/${noteId}`),
  createNote: (data: { title: string; content?: string; folder_id?: string }) =>
    api.post<{ status: string; data: KBNote }>("/kb/notes", data),
  updateNote: (
    noteId: string,
    data: { title?: string; content?: string; folder_id?: string },
  ) => api.put<{ status: string; data: KBNote }>(`/kb/notes/${noteId}`, data),
  deleteNote: (noteId: string) =>
    api.delete<{ status: string }>(`/kb/notes/${noteId}`),
  searchNotes: (q: string) =>
    api.get<{ status: string; data: KBNoteListItem[] }>("/kb/notes/search", {
      params: { q },
    }),

  // Wikilink
  getBacklinks: (noteId: string) =>
    api.get<{ status: string; data: BacklinkItem[] }>(
      `/kb/wikilink/backlinks/${noteId}`,
    ),
  getGraph: () =>
    api.get<{
      status: string;
      data: { nodes: GraphNode[]; edges: GraphEdge[] };
    }>("/kb/wikilink/graph"),

  // Auto-organize
  autoOrganize: (data: {
    kp_id: string;
    title: string;
    content: string;
    tags?: string[];
    subject?: string;
    action?: "learn" | "quiz" | "review";
  }) =>
    api.post<{
      status: string;
      data: { note_id: string; title: string; folder_id: string };
    }>("/kb/auto-organize", data),
  batchOrganize: (
    items: Array<{
      kp_id: string;
      title: string;
      content: string;
      tags?: string[];
      subject?: string;
      action?: "learn" | "quiz" | "review";
    }>,
  ) =>
    api.post<{
      status: string;
      data: Array<{ note_id: string; title: string; folder_id: string }>;
    }>("/kb/batch-organize", items),
};
