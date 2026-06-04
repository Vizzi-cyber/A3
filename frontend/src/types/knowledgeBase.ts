export interface KBFolder {
  folder_id: string;
  name: string;
  parent_id: string | null;
  created_at: string | null;
}

export interface KBNote {
  note_id: string;
  title: string;
  content: string;
  folder_id: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface KBNoteListItem {
  note_id: string;
  title: string;
  content_preview: string;
  folder_id: string | null;
  updated_at: string | null;
}

export interface BacklinkItem {
  note_id: string;
  title: string;
  excerpt: string;
}

export interface GraphNode {
  id: string;
  title: string;
}

export interface GraphEdge {
  source: string;
  target: string;
}
