import React from 'react'
import { Button, Result } from 'antd'
import { useNavigate } from 'react-router-dom'
import { HomeOutlined } from '@ant-design/icons'

const NotFound: React.FC = () => {
  const navigate = useNavigate()
  return (
    <div className="flex items-center justify-center min-h-[70vh]">
      <Result
        status="404"
        title={<span className="text-slate-800 font-bold">404</span>}
        subTitle={<span className="text-slate-500">抱歉，你访问的页面不存在</span>}
        extra={
          <Button
            type="primary"
            size="large"
            icon={<HomeOutlined />}
            onClick={() => navigate('/')}
            className="rounded-full bg-primary border-0 shadow-md hover:shadow-lg"
          >
            返回首页
          </Button>
        }
      />
    </div>
  )
}

export default NotFound
