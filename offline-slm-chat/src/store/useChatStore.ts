import { create } from 'zustand'

interface ChatState {
  activeConversationId: string | null;
  setActiveConversationId: (id: string | null) => void;
  isGenerating: boolean;
  setIsGenerating: (isGenerating: boolean) => void;
  streamingContent: string;
  setStreamingContent: (content: string) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  activeConversationId: null,
  setActiveConversationId: (id) => set({ activeConversationId: id }),
  isGenerating: false,
  setIsGenerating: (isGenerating) => set({ isGenerating }),
  streamingContent: '',
  setStreamingContent: (content) => set({ streamingContent: content }),
}))
