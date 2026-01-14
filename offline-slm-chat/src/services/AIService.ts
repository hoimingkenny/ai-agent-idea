import { initLlama, LlamaContext } from 'llama.rn';
import { getModelPath, checkFileExists, downloadModel } from './FileSystem';

class AIService {
  private context: LlamaContext | undefined;
  private isModelLoaded = false;

  async loadModel(filename: string) {
    if (this.isModelLoaded) return;
    
    const exists = await checkFileExists(filename);
    if (!exists) {
      console.log(`Model ${filename} not found. Downloading...`);
      // Fallback URL for the default model
      const DEFAULT_MODEL_URL = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf";
      
      if (filename === 'tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf') {
           const uri = await downloadModel(DEFAULT_MODEL_URL, filename, (p) => {
               console.log(`Downloading ${filename}: ${(p * 100).toFixed(1)}%`);
           });
           if (!uri) throw new Error("Download failed");
      } else {
          throw new Error(`Model file ${filename} missing.`);
      }
    }

    const path = getModelPath(filename);
    try {
      this.context = await initLlama({
        model: path,
        use_mlock: true,
        n_ctx: 2048,
        // n_gpu_layers: 0 // Auto by default
      });
      this.isModelLoaded = true;
      console.log("Model loaded");
    } catch (e) {
      console.error("Failed to load model", e);
      throw e;
    }
  }

  async unloadModel() {
    if (this.context) {
      await this.context.release();
      this.context = undefined;
      this.isModelLoaded = false;
      console.log("Model unloaded");
    }
  }

  async streamResponse(prompt: string, onToken: (token: string) => void) {
    if (!this.context) throw new Error("Model not loaded");
    
    try {
        await this.context.completion({
            prompt,
            n_predict: 512,
            stop: ["User:", "\n\n"] // Basic stop sequences
        }, (data) => {
            onToken(data.token);
        });
    } catch (e) {
        console.error("Inference error", e);
        throw e;
    }
  }
}

export const aiService = new AIService();
