import NetInfo from '@react-native-community/netinfo';
import database from '../database';

export class SyncService {
    static async sync() {
        const state = await NetInfo.fetch();
        if (!state.isConnected) {
            console.log("Offline, skipping sync");
            return;
        }
        
        console.log("Syncing with cloud...");
        // TODO: Implement WatermelonDB sync protocol
        // await synchronize({
        //   database,
        //   pullChanges: async ({ lastPulledAt }) => { ... },
        //   pushChanges: async ({ changes, lastPulledAt }) => { ... },
        // })
    }
}
