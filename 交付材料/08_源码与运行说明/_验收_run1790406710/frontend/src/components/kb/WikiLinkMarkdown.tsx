import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { resolveWikilink } from "../../lib/wikilinkParser";

interface WikiLinkMarkdownProps {
  content: string;
  notes: { note_id: string; title: string }[];
  onNoteClick?: (noteId: string) => void;
}

const WikiLinkMarkdown: React.FC<WikiLinkMarkdownProps> = ({
  content,
  notes,
  onNoteClick,
}) => {
  const processContent = (text: string): string => {
    return text.replace(
      /\[\[([^\[\]|#]+?)(?:#[^\[\]|]*)?(?:\|[^\[\]]*?)?\]\]/g,
      (_match, target) => {
        const noteId = resolveWikilink(target.trim(), notes);
        if (noteId) {
          return `[${target.trim()}](#wikilink:${noteId})`;
        }
        return `**${target.trim()}**`;
      },
    );
  };

  const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const target = e.target as HTMLElement;
    if (target.tagName === "A") {
      const href = target.getAttribute("href");
      if (href?.startsWith("#wikilink:")) {
        e.preventDefault();
        const noteId = href.replace("#wikilink:", "");
        onNoteClick?.(noteId);
      }
    }
  };

  return (
    <div
      className="markdown-preview prose prose-slate max-w-none"
      onClick={handleClick}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {processContent(content)}
      </ReactMarkdown>
    </div>
  );
};

export default WikiLinkMarkdown;
