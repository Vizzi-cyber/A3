import React, { Suspense, lazy } from "react";
import { Spin } from "antd";

const MonacoEditor = lazy(() => import("@monaco-editor/react"));

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  language?: string;
  height?: string;
  readOnly?: boolean;
}

const CodeEditor: React.FC<CodeEditorProps> = ({
  value,
  onChange,
  language = "c",
  height = "300px",
  readOnly = false,
}) => {
  return (
    <div className="rounded-xl overflow-hidden" style={{ height }}>
      <Suspense
        fallback={
          <div
            className="flex items-center justify-center bg-slate-900 text-slate-400"
            style={{ height }}
          >
            <Spin tip="加载编辑器中..." />
          </div>
        }
      >
        <MonacoEditor
          height={height}
          language={language === "C" || language === "c" ? "c" : "python"}
          value={value}
          onChange={(val) => onChange(val || "")}
          theme="vs-dark"
          options={{
            readOnly,
            minimap: { enabled: false },
            fontSize: 14,
            fontFamily:
              "'JetBrains Mono', 'Fira Code', 'Cascadia Code', Consolas, monospace",
            lineNumbers: "on",
            bracketPairColorization: { enabled: true },
            autoClosingBrackets: "always",
            autoIndent: "full",
            formatOnPaste: true,
            tabSize: 4,
            scrollBeyondLastLine: false,
            smoothScrolling: true,
            cursorBlinking: "smooth",
            renderLineHighlight: "all",
            padding: { top: 12, bottom: 12 },
            suggestOnTriggerCharacters: true,
            wordWrap: "on",
          }}
        />
      </Suspense>
    </div>
  );
};

export default CodeEditor;
