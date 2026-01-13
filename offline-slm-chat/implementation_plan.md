# Technical Implementation Plan: Offline-First AI Mobile App with SLM

## 1. Project Summary
**Goal:** Build a privacy-focused, offline-first mobile application that runs Small Language Models (SLMs) directly on the device.
**Core Value Proposition:** This application eliminates API costs and ensures complete user privacy by processing all data locally. It demonstrates advanced engineering capabilities in resource optimization, managing memory pressure, and handling edge-AI constraints (quantization, battery usage) on mobile hardware.

## 2. Technical Architecture & Stack

### Stack Selection
| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Framework** | **React Native** (Expo) | Cross-platform (iOS/Android), huge ecosystem, and easy integration with native modules via JSI. |
| **Language** | **TypeScript** | Type safety is critical for complex state management and data schemas. |
| **AI Engine** | **llama.rn** (llama.cpp bindings) | The industry standard for running GGUF models on edge. Natively supports 4-bit/8-bit quantization and CPU/GPU offloading. |
| **Local DB** | **WatermelonDB** | Built for offline-first apps. High performance (lazy loading) and built-in sync primitives. |
| **State Mgmt** | **Zustand** | Lightweight, supports transient updates (vital for streaming tokens without re-rendering the whole tree). |
| **Storage** | **MMKV** | Fast, synchronous storage for user preferences and model configuration (not chat history). |

### Architecture Diagram

```mermaid
graph TD
    subgraph UI_Layer
        ChatInterface[Chat Interface]
        Settings[Settings & Model Config]
    end

    subgraph Logic_Layer
        Orchestrator[App Orchestrator]
        ContextMgr[Context Manager\n(Sliding Window)]
        BatteryMgr[Battery Monitor]
        MemoryMgr[Memory Monitor]
    end

    subgraph Data_Layer
        WatermelonDB[(WatermelonDB\nEncrypted Store)]
        VectorStore[(Local Vector Store)]
    end

    subgraph AI_Engine
        ModelLoader[Model Loader\n(Lazy/Unload)]
        Inference[Inference Engine\n(llama.rn)]
    end

    ChatInterface --> Orchestrator
    Orchestrator --> ContextMgr
    ContextMgr --> WatermelonDB
    ContextMgr --> VectorStore
    
    Orchestrator --> ModelLoader
    ModelLoader --> Inference
    
    BatteryMgr -.->|Throttle/Defer| Inference
    MemoryMgr -.->|Trigger Unload| ModelLoader
    
    Inference -->|Stream Tokens| ChatInterface
```

### Data Schemas

**1. Database Models (WatermelonDB)**
```typescript
// schema.ts
import { appSchema, tableSchema } from '@nozbe/watermelondb'

export const mySchema = appSchema({
  version: 1,
  tables: [
    tableSchema({
      name: 'conversations',
      columns: [
        { name: 'title', type: 'string' },
        { name: 'created_at', type: 'number' },
        { name: 'archived', type: 'boolean' },
      ],
    }),
    tableSchema({
      name: 'messages',
      columns: [
        { name: 'conversation_id', type: 'string', isIndexed: true },
        { name: 'content', type: 'string' },
        { name: 'role', type: 'string' }, // 'user' | 'assistant'
        { name: 'is_embedded', type: 'boolean' },
        { name: 'created_at', type: 'number' },
      ],
    }),
  ],
})
```

**2. Application State**
```typescript
interface SystemStatus {
  batteryLevel: number;
  isCharging: boolean;
  availableMemory: number; // in MB
  modelState: 'unloaded' | 'loading' | 'ready' | 'generating';
}

interface ModelConfig {
  filename: string;
  quantization: 'q4_0' | 'q8_0';
  contextSize: number;
}
```

### Architecture Mapping
| Architectural Decision | Phase | Implementation Strategy |
|------------------------|-------|-------------------------|
| **Model Management** | Phase 2 | `ModelService` class handles initialization. `AppState` listeners trigger unload on background. |
| **Context Window** | Phase 3 | `ContextManager` utilizes a sliding window algorithm. Old messages are summarized or dropped based on token count. |
| **Quantization Strategy**| Phase 3 | `HardwareProfiler` runs on startup. Selects `q4_0` model for <4GB RAM, `q8_0` for >6GB RAM. |
| **Battery Optimization**| Phase 3 | `BatteryMonitor` hook intercepts inference requests. Throttles token generation speed or pauses background tasks. |
| **Offline-first Sync** | Phase 4 | WatermelonDB sync protocol. Local encryption via SQLCipher integration. |

---

## 3. Detailed Implementation Plan

### Phase 1: Foundation & Data Layer
**Goal:** Set up the React Native environment, offline database, and basic UI shell.
**File Structure:**
```
src/
  ├── database/
  │   ├── schema.ts
  │   ├── models/
  │   │   ├── Conversation.ts
  │   │   └── Message.ts
  │   └── index.ts
  ├── store/
  │   └── useChatStore.ts
  └── ui/
      └── screens/
          └── ChatScreen.tsx
```
**Key Tasks:**
1.  **Initialize Project**: `npx create-expo-app` (with native code support).
2.  **Database Setup**: Implement WatermelonDB with the schema defined above.
3.  **UI Skeleton**: Build a basic chat interface (bubble list, input field) using React Native components.

### Phase 2: Core Logic & Inference
**Goal:** Successfully load a model and generate text on-device.
**File Structure:**
```
src/
  ├── services/
  │   ├── AIService.ts
  │   └── FileSystem.ts
```
**Key Tasks:**
1.  **Model Integration**: Install `llama.rn`. Implement `loadModel(path)` function.
2.  **Model Download**: Implement a downloader to fetch GGUF models (e.g., TinyLlama or Phi-3) to the document directory.
3.  **Inference Loop**: Create `generateResponse(prompt)` utilizing async iterators for token streaming.
4.  **Connect UI**: Hook up the `ChatScreen` to trigger `generateResponse` and display streaming tokens.

### Phase 3: Optimization & Intelligence
**Goal:** Implement the "Smart" features: memory management, context window, and battery awareness.
**File Structure:**
```
src/
  ├── logic/
  │   ├── ContextPruner.ts
  │   ├── HardwareProfiler.ts
  │   └── BatteryGuard.ts
```
**Key Tasks:**
1.  **Dynamic Quantization**: Implement `HardwareProfiler.detectCapabilities()` to decide which model file to load.
2.  **Context Management**: Implement `ContextPruner.buildPrompt(messages, limit)` which takes the conversation history and ensures it fits within the context window (e.g., 2048 tokens).
3.  **Lazy Loading**: Modify `AIService` to unload the model after `n` minutes of inactivity using `setTimeout` and `AppState` change listeners.
4.  **Battery Guard**: Use `expo-battery`. If `batteryLevel < 0.20` and `!isCharging`, show a warning or switch to a smaller/faster model config.

### Phase 4: Polish & Security
**Goal:** Secure user data and ensure robust offline/online transitions.
**File Structure:**
```
src/
  ├── sync/
  │   └── SyncService.ts
  └── security/
      └── Encryption.ts
```
**Key Tasks:**
1.  **Encryption**: Integrate SQLCipher or an encrypted storage adapter for WatermelonDB.
2.  **Sync Logic**: Implement a basic sync loop that checks for network connectivity (`NetInfo`) before attempting to push changes to a mock backend or user-defined endpoint.
3.  **UI Refinement**: Add loading states, error handling for "Out of Memory" crashes, and markdown rendering for bot responses.

---

## 4. Development Priorities

*   **P0 (Critical)**:
    *   Setup React Native + WatermelonDB.
    *   Load and run a basic GGUF model (e.g., TinyLlama) via `llama.rn`.
    *   Basic chat UI with streaming responses.
*   **P1 (Important)**:
    *   Context Window management (prevent crashing on long chats).
    *   Model unloading to free RAM when app is backgrounded.
    *   Hardware profiling for auto-selection of quantization.
*   **P2 (Nice-to-have)**:
    *   Battery-aware throttling.
    *   Semantic embedding/RAG for long-term memory.
    *   Cloud sync functionality.
