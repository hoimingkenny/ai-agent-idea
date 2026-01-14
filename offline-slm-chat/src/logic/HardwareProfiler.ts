import * as Device from 'expo-device';

export class HardwareProfiler {
    static async getRecommendedModelConfig() {
        // Note: maxMemoryAsync might not be available on all platforms/devices or requires specific permissions
        // Defaulting to a conservative estimate if unavailable.
        // On iOS, os-level memory info is restricted.
        
        let totalMemory = 4 * 1024 * 1024 * 1024; // Default 4GB
        
        // Use Device.totalMemory if available (added in recent Expo versions)
        if (Device.totalMemory) {
            totalMemory = Device.totalMemory;
        }

        const memoryGB = totalMemory / (1024 * 1024 * 1024);
        
        if (memoryGB < 4) {
             return { quantization: 'q4_0', contextSize: 1024 };
        } else {
             return { quantization: 'q8_0', contextSize: 2048 };
        }
    }
}
