import React from 'react';
import { StatusBar } from 'expo-status-bar';
import ChatScreen from './src/ui/screens/ChatScreen';
import { SafeAreaProvider } from 'react-native-safe-area-context';

export default function App() {
  return (
    <SafeAreaProvider>
      <ChatScreen />
      <StatusBar style="auto" />
    </SafeAreaProvider>
  );
}
