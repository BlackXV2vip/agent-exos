import type { ElectronAPI } from "../preload/types"

declare global {
  interface Window {
    api: ElectronAPI
    __EXOS_AGENT__?: {
      deepLinks?: string[]
    }
  }
}
