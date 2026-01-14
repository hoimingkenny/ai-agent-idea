import * as Battery from 'expo-battery';

export class BatteryGuard {
    static async checkBatteryStatus() {
        try {
            const level = await Battery.getBatteryLevelAsync();
            const state = await Battery.getBatteryStateAsync();
            
            // level is between 0 and 1. -1 if unavailable.
            if (level === -1) return { throttle: false };

            const isCharging = state === Battery.BatteryState.CHARGING || state === Battery.BatteryState.FULL;
            
            if (level < 0.2 && !isCharging) {
                return { throttle: true, warning: "Low battery" };
            }
        } catch (e) {
            console.warn("Battery check failed", e);
        }
        return { throttle: false };
    }
}
