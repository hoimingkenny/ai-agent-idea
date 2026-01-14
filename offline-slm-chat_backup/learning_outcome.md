# Learning Outcomes & Portfolio Guide: Offline-First AI Chat

## 1. Project Challenges

*   **Managing High Memory Pressure on Mobile Constraints:**
    Running Large Language Models (even "Small" ones) pushes mobile hardware to its limit. The challenge wasn't just loading the model, but preventing the OS from killing the app due to OOM (Out of Memory) errors. I had to implement aggressive memory management strategies, such as listening to `AppState` changes to unload the model immediately when backgrounded and lazy-loading it only when inference is strictly required.

*   **Balancing Inference Latency with Battery Efficiency:**
    Continuous token generation drains battery rapidly. I had to build a `BatteryMonitor` system that intercepts inference requests. The challenge was creating a feedback loop that detects low battery states (<20%) or lack of charging and automatically throttles token generation speed or switches to a more efficient, lower-quality model quantization to preserve device longevity.

*   **Implementing Efficient Context Management Locally:**
    Without a massive cloud context window, hitting the token limit (e.g., 2048 tokens) causes immediate crashes or incoherent responses. I had to engineer a `ContextPruner` using a sliding window algorithm. The difficulty lay in determining which messages to drop while preserving the semantic thread of the conversation, requiring a robust calculation of token counts on the client side before every inference pass.

## 2. The "Why" (Problem Solved)

**Privacy, Autonomy, and Cost-Efficiency.**

*   **Absolute Privacy:** In an era of data leakage, this project ensures that sensitive personal data *never* leaves the user's device. There is zero risk of data harvesting by third-party API providers.
*   **Zero-Cost Scalability:** By offloading compute to the edge (the user's device), the business eliminates the exponential cost of cloud GPU inference (API token costs).
*   **Universal Availability:** The application provides intelligence in "air-gapped" environments—planes, subways, or remote locations with poor connectivity—where cloud-dependent AI assistants fail.

## 3. CV/Resume Summary

**Offline-First On-Device AI Mobile Application**
*React Native, TypeScript, llama.rn, WatermelonDB, Zustand*

Architected a privacy-focused mobile application capable of running quantized Small Language Models (SLMs) directly on-device using **llama.rn**. Engineered a custom **Hardware Profiler** to dynamically select model quantization (q4_0 vs q8_0) based on real-time RAM usage, optimizing inference stability on constrained hardware. Implemented a robust offline-first architecture with **WatermelonDB** and **Zustand**, ensuring smooth 60fps UI performance even during heavy concurrent inference and token streaming.

## 4. Key Learning Outcomes (Star Method Prep)

*   **Edge AI & Resource Optimization:**
    *   Demonstrated ability to profile mobile hardware limits and implement dynamic adaptation strategies (switching model quantization at runtime) to prevent OOM crashes on older devices.

*   **Advanced React Native Performance:**
    *   Mastered the use of **JSI (JavaScript Interface)** bindings for synchronous native communication and utilized **Zustand** for transient state updates, preventing unnecessary React re-renders during high-frequency token streaming.

*   **Offline-First Architecture Design:**
    *   Gained deep expertise in local-first data synchronization and persistence using **WatermelonDB**, handling complex schema migrations and ensuring data integrity without reliable network access.
