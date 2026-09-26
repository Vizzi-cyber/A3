declare module 'react-syntax-highlighter' {
  import { ComponentType } from 'react'
  export const Prism: ComponentType<any>
  export const Light: ComponentType<any>
}

declare module 'react-syntax-highlighter/dist/esm/styles/prism' {
  export const vscDarkPlus: any
  export const oneDark: any
  export const oneLight: any
}

declare module 'react-syntax-highlighter/dist/cjs/styles/prism' {
  export const vscDarkPlus: any
}
