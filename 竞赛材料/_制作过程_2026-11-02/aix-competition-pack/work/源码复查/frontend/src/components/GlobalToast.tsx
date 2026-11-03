import React, { useEffect } from 'react'
import { message } from 'antd'
import { useAppStore } from '../store'

const GlobalToast: React.FC = () => {
  const toast = useAppStore((s) => s.toast)
  const setToast = useAppStore((s) => s.setToast)

  useEffect(() => {
    if (toast) {
      message[toast.type](toast.message)
      setToast(null)
    }
  }, [toast, setToast])

  return null
}

export default GlobalToast
