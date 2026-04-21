import React, { useRef, useEffect, useState, useCallback } from 'react'
import {
  Button,
  Input,
  Avatar,
  Badge,
  Space,
  Tag,
  Typography,
  Spin,
  Tooltip,
  Modal,
} from 'antd'
import {
  SendOutlined,
  RobotOutlined,
  UserOutlined,
  BulbOutlined,
  LoadingOutlined,
  PictureOutlined,
  CloseOutlined,
  LinkOutlined,
  UploadOutlined,
} from '@ant-design/icons'
import type { ChatMessage, VisionContentItem } from '../types'

interface ChatPanelProps {
  messages: ChatMessage[]
  loading: boolean
  onSend: (content: string | VisionContentItem[]) => void
  placeholder?: string
  suggestions?: string[]
  showAvatars?: boolean
  showSuggestions?: boolean
  title?: string
  subtitle?: string
  tag?: string
  extraHeader?: React.ReactNode
  inputPrefix?: React.ReactNode
  className?: string
  style?: React.CSSProperties
}

export const ChatPanel: React.FC<ChatPanelProps> = ({
  messages,
  loading,
  onSend,
  placeholder = '输入消息...',
  suggestions = [],
  showAvatars = true,
  showSuggestions = false,
  title = 'AI 助手',
  subtitle = '',
  tag = '在线',
  extraHeader,
  inputPrefix,
  className = '',
  style,
}) => {
  const [inputValue, setInputValue] = React.useState('')
  const [attachedImages, setAttachedImages] = useState<string[]>([])
  const [imageModalOpen, setImageModalOpen] = useState(false)
  const [imageUrlInput, setImageUrlInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const buildContent = (): string | VisionContentItem[] => {
    if (attachedImages.length === 0) {
      return inputValue.trim()
    }
    const content: VisionContentItem[] = []
    if (inputValue.trim()) {
      content.push({ type: 'text', text: inputValue.trim() })
    }
    attachedImages.forEach((url) => {
      content.push({ type: 'image_url', image_url: { url } })
    })
    return content
  }

  const handleSend = () => {
    const content = buildContent()
    if (
      (typeof content === 'string' && !content.trim()) ||
      (Array.isArray(content) && content.length === 0)
    ) {
      return
    }
    onSend(content)
    setInputValue('')
    setAttachedImages([])
  }

  const handlePaste = useCallback(
    (e: React.ClipboardEvent) => {
      const items = e.clipboardData?.items
      if (!items) return
      for (let i = 0; i < items.length; i++) {
        const item = items[i]
        if (item.type.startsWith('image/')) {
          const blob = item.getAsFile()
          if (blob) {
            const reader = new FileReader()
            reader.onload = (ev) => {
              const result = ev.target?.result as string
              if (result) setAttachedImages((prev) => [...prev, result])
            }
            reader.readAsDataURL(blob)
          }
          e.preventDefault()
        }
      }
    },
    []
  )

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files) return
    Array.from(files).forEach((file) => {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader()
        reader.onload = (ev) => {
          const result = ev.target?.result as string
          if (result) setAttachedImages((prev) => [...prev, result])
        }
        reader.readAsDataURL(file)
      }
    })
    e.target.value = ''
  }

  const handleAddUrl = () => {
    const url = imageUrlInput.trim()
    if (!url) return
    setAttachedImages((prev) => [...prev, url])
    setImageUrlInput('')
    setImageModalOpen(false)
  }

  const renderMessageContent = (msg: ChatMessage) => {
    if (typeof msg.content === 'string') {
      return msg.content
    }
    return (
      <div className="space-y-2">
        {msg.content.map((item, idx) => {
          if (item.type === 'text') {
            return <div key={idx}>{item.text}</div>
          }
          if (item.type === 'image_url') {
            return (
              <img
                key={idx}
                src={item.image_url.url}
                alt="attached"
                className="max-w-[200px] max-h-[200px] rounded-lg border border-slate-200 object-cover cursor-pointer"
                onClick={() => window.open(item.image_url.url, '_blank')}
              />
            )
          }
          return null
        })}
      </div>
    )
  }

  return (
    <div className={`flex flex-col h-full min-h-0 ${className}`} style={style}>
      {title && (
        <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
          <Space>
            <Badge dot color="green">
              <Avatar icon={<RobotOutlined />} className="bg-gradient-to-br from-primary to-secondary shadow-glow" />
            </Badge>
            <div>
              <Typography.Text className="font-bold text-slate-800 block">{title}</Typography.Text>
              {subtitle && <Typography.Text className="text-xs text-slate-400">{subtitle}</Typography.Text>}
            </div>
          </Space>
          <Space>
            {tag && <Tag color="success" className="rounded-full border-0 bg-emerald-50 text-emerald-600">{tag}</Tag>}
            {extraHeader}
          </Space>
        </div>
      )}

      <div className="flex-1 overflow-y-auto pr-2 space-y-5 mb-4 flex flex-col justify-end min-h-0">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {showAvatars ? (
              <Space align="start" size={10}>
                {msg.role === 'ai' && (
                  <Avatar icon={<RobotOutlined />} className="bg-gradient-to-br from-primary to-secondary shadow-glow shrink-0" />
                )}
                <div
                  className={`max-w-md px-4 py-3 text-sm leading-relaxed ${
                    msg.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-ai'
                  }`}
                >
                  {renderMessageContent(msg)}
                </div>
                {msg.role === 'user' && (
                  <Avatar icon={<UserOutlined />} className="bg-slate-200 text-slate-500 shrink-0" />
                )}
              </Space>
            ) : (
              <div
                className={`max-w-[85%] px-4 py-3 text-sm leading-relaxed ${
                  msg.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-ai'
                }`}
              >
                {renderMessageContent(msg)}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <Space align="start" size={10}>
              {showAvatars && <Avatar icon={<RobotOutlined />} className="bg-gradient-to-br from-primary to-secondary shadow-glow shrink-0" />}
              <div className="chat-bubble-ai px-4 py-3 flex items-center gap-2">
                <LoadingOutlined className="text-primary" />
                <span className="text-sm text-slate-500">思考中...</span>
              </div>
            </Space>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="space-y-3 pt-3 border-t border-slate-100">
        {attachedImages.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {attachedImages.map((url, i) => (
              <div key={i} className="relative group">
                <img
                  src={url}
                  alt={`attach-${i}`}
                  className="w-16 h-16 rounded-lg border border-slate-200 object-cover"
                />
                <button
                  className="absolute -top-1.5 -right-1.5 w-4 h-4 bg-red-500 text-white rounded-full text-[10px] flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                  onClick={() => setAttachedImages((prev) => prev.filter((_, idx) => idx !== i))}
                >
                  <CloseOutlined />
                </button>
              </div>
            ))}
          </div>
        )}

        {showSuggestions && suggestions.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {suggestions.map((s, i) => (
              <Button
                key={i}
                size="small"
                className="rounded-full text-xs border-slate-200 bg-slate-50 hover:bg-indigo-50 hover:text-primary hover:border-indigo-200 transition-all"
                onClick={() => { setInputValue(s); onSend(s) }}
              >
                <BulbOutlined /> {s}
              </Button>
            ))}
          </div>
        )}

        <Space.Compact className="w-full">
          <Tooltip title="添加图片">
            <Button
              icon={<PictureOutlined />}
              onClick={() => setImageModalOpen(true)}
              className="rounded-l-xl border-r-0 bg-slate-50"
            />
          </Tooltip>
          <Input
            placeholder={placeholder}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onPressEnter={handleSend}
            onPaste={handlePaste}
            className="bg-slate-50 border-slate-200 focus:bg-white transition-colors"
            prefix={inputPrefix}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            loading={loading}
            onClick={handleSend}
            className="rounded-r-xl bg-primary border-0 shadow-md hover:shadow-lg"
          >
            发送
          </Button>
        </Space.Compact>
      </div>

      <Modal
        title="添加图片"
        open={imageModalOpen}
        onCancel={() => { setImageModalOpen(false); setImageUrlInput('') }}
        onOk={handleAddUrl}
        okText="添加"
        cancelText="取消"
      >
        <div className="space-y-4">
          <div>
            <Typography.Text className="block mb-1 text-sm text-slate-600">图片链接</Typography.Text>
            <Input
              placeholder="https://..."
              value={imageUrlInput}
              onChange={(e) => setImageUrlInput(e.target.value)}
              onPressEnter={handleAddUrl}
              prefix={<LinkOutlined />}
            />
          </div>
          <div>
            <Typography.Text className="block mb-1 text-sm text-slate-600">或上传本地图片</Typography.Text>
            <Button
              icon={<UploadOutlined />}
              onClick={() => fileInputRef.current?.click()}
              className="w-full"
            >
              选择文件
            </Button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              multiple
              className="hidden"
              onChange={handleFileChange}
            />
          </div>
          <Typography.Text className="text-xs text-slate-400 block">
            提示：也可以直接在输入框中粘贴图片（Ctrl+V）
          </Typography.Text>
        </div>
      </Modal>
    </div>
  )
}
