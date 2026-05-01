import React, { useState, ReactNode, useMemo } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { CopyOutlined, CheckOutlined } from '@ant-design/icons'
import { message } from 'antd'

interface MarkdownViewerProps {
  content: string
  className?: string
}

/** 从 ReactNode 提取纯文本 —— 模块级，避免每次渲染重新创建 */
function extractText(node: ReactNode): string {
  if (node == null) return ''
  if (typeof node === 'string') return node
  if (typeof node === 'number') return String(node)
  if (Array.isArray(node)) return node.map(extractText).join('')
  if (React.isValidElement(node)) {
    return extractText(node.props.children)
  }
  return ''
}

const CodeBlock: React.FC<{ language: string; children: string }> = ({ language, children }) => {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(children)
      setCopied(true)
      message.success('代码已复制')
      setTimeout(() => setCopied(false), 2000)
    } catch {
      message.error('复制失败')
    }
  }

  const langLabel = language || 'text'

  return (
    <div className="code-block-wrapper my-4 rounded-lg overflow-hidden border border-slate-200 shadow-sm">
      <div className="code-header flex items-center justify-between px-4 py-2 bg-slate-800 text-slate-300 text-xs">
        <span className="font-mono font-medium">{langLabel}</span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 px-2 py-1 rounded hover:bg-slate-700 transition-colors"
          title="复制代码"
        >
          {copied ? <CheckOutlined className="text-success" /> : <CopyOutlined />}
          <span>{copied ? '已复制' : '复制'}</span>
        </button>
      </div>
      <SyntaxHighlighter
        language={langLabel === 'c' ? 'c' : langLabel}
        style={vscDarkPlus}
        customStyle={{
          margin: 0,
          padding: '1rem 1.25rem',
          fontSize: '13.5px',
          lineHeight: '1.7',
          background: '#1e1e1e',
        }}
        showLineNumbers
        lineNumberStyle={{
          color: '#6e7681',
          fontSize: '12px',
          paddingRight: '1rem',
          minWidth: '2.5rem',
        }}
      >
        {children}
      </SyntaxHighlighter>
    </div>
  )
}

/** 静态 components 映射 —— 模块级单例，避免每次渲染重新创建对象 */
const markdownComponents = {
  code({ inline, className: cls, children, ...props }: any) {
    const match = /language-(\w+)/.exec(cls || '')
    const codeText = extractText(children)
    if (!inline && match) {
      return <CodeBlock language={match[1]}>{codeText}</CodeBlock>
    }
    return (
      <code className="inline-code" {...props}>
        {codeText}
      </code>
    )
  },
  h1({ children }: any) {
    return <h1 className="md-h1">{children}</h1>
  },
  h2({ children }: any) {
    return <h2 className="md-h2">{children}</h2>
  },
  h3({ children }: any) {
    return <h3 className="md-h3">{children}</h3>
  },
  h4({ children }: any) {
    return <h4 className="md-h4">{children}</h4>
  },
  p({ children }: any) {
    return <p className="md-p">{children}</p>
  },
  strong({ children }: any) {
    const text = extractText(children)
    if (text.startsWith('例')) {
      return <span className="example-title">{children}</span>
    }
    return <strong className="md-strong">{children}</strong>
  },
  ul({ children }: any) {
    return <ul className="md-ul">{children}</ul>
  },
  ol({ children }: any) {
    return <ol className="md-ol">{children}</ol>
  },
  li({ children }: any) {
    return <li className="md-li">{children}</li>
  },
  blockquote({ children }: any) {
    return <blockquote className="md-blockquote">{children}</blockquote>
  },
  table({ children }: any) {
    return (
      <div className="table-wrapper">
        <table className="md-table">{children}</table>
      </div>
    )
  },
  hr() {
    return <hr className="md-hr" />
  },
}

/** 模块级常量，避免每次渲染创建新数组 */
const remarkPlugins = [remarkGfm as any]

export const MarkdownViewer: React.FC<MarkdownViewerProps> = ({ content, className = '' }) => {
  if (!content) {
    return <div className="text-slate-400 text-center py-12">内容加载中...</div>
  }

  return (
    <div className={`markdown-body ${className}`}>
      <ReactMarkdown
        remarkPlugins={remarkPlugins}
        components={markdownComponents}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}

export default MarkdownViewer
