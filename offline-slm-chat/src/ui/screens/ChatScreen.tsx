import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, FlatList, StyleSheet, SafeAreaView } from 'react-native';
import { useChatStore } from '../../store/useChatStore';
import database from '../../database';
import { Q } from '@nozbe/watermelondb';
import Message from '../../database/models/Message';

import { aiService } from '../../services/AIService';
import { ContextPruner } from '../../logic/ContextPruner';

// Placeholder for message item
const MessageItem = ({ content, role }: { content: string, role: 'user' | 'assistant' }) => (
  <View style={[
    styles.messageBubble,
    role === 'user' ? styles.userBubble : styles.assistantBubble
  ]}>
    <Text style={[styles.messageText, role === 'user' && styles.userMessageText]}>{content}</Text>
  </View>
);

export default function ChatScreen() {
  const { activeConversationId, setActiveConversationId, isGenerating, setIsGenerating, streamingContent, setStreamingContent } = useChatStore();
  const [inputText, setInputText] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);

  useEffect(() => {
    // Load messages when conversation changes
    const loadMessages = async () => {
      if (!activeConversationId) {
          setMessages([]);
          return;
      }
      try {
        const conversation = await database.get('conversations').find(activeConversationId);
        // @ts-ignore
        const msgs = await conversation.messages.fetch();
        setMessages(msgs);
      } catch (e) {
          console.error("Failed to load conversation", e);
      }
    };
    loadMessages();
  }, [activeConversationId]);

  const handleSend = async () => {
    if (!inputText.trim() || isGenerating) return;
    
    const text = inputText;
    setInputText('');
    
    let conversationId = activeConversationId;

    try {
      await database.write(async () => {
        let conversation;
        if (!conversationId) {
            conversation = await database.get('conversations').create((c: any) => {
                c.title = text.substring(0, 20);
                c.createdAt = new Date();
                c.archived = false;
            });
            conversationId = conversation.id;
            setActiveConversationId(conversationId);
        } else {
            conversation = await database.get('conversations').find(conversationId);
        }

        // Create user message
        await database.get('messages').create((m: any) => {
            m.conversation.set(conversation);
            m.content = text;
            m.role = 'user';
            m.createdAt = new Date();
            m.isEmbedded = false;
        });
      });

      // Refresh messages
      // Note: With Observables this would be automatic. For now manual refresh.
      if (conversationId) {
          const conv = await database.get('conversations').find(conversationId);
          // @ts-ignore
          const msgs = await conv.messages.fetch();
          setMessages(msgs);
      }

      // Start Inference
      setIsGenerating(true);
      setStreamingContent('');

      // Auto-load model if needed (hardcoded filename for demo)
      await aiService.loadModel('tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf');

      const promptMessages = [...messages, { role: 'user', content: text }];
      const prompt = ContextPruner.buildPrompt(promptMessages);

      let fullResponse = '';
      await aiService.streamResponse(prompt + "Assistant:", (token) => {
          fullResponse += token;
          setStreamingContent(fullResponse);
      });

      // Save assistant message
      await database.write(async () => {
          const conversation = await database.get('conversations').find(conversationId!);
          await database.get('messages').create((m: any) => {
              m.conversation.set(conversation);
              m.content = fullResponse;
              m.role = 'assistant';
              m.createdAt = new Date();
              m.isEmbedded = false;
          });
      });

      // Refresh messages again
      if (conversationId) {
        const conv = await database.get('conversations').find(conversationId);
        // @ts-ignore
        const msgs = await conv.messages.fetch();
        setMessages(msgs);
      }

    } catch (e) {
        console.error("Error sending message:", e);
    } finally {
        setIsGenerating(false);
        setStreamingContent('');
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <FlatList
        data={messages}
        keyExtractor={item => item.id}
        renderItem={({ item }) => <MessageItem content={item.content} role={item.role} />}
        ListFooterComponent={
          isGenerating ? <MessageItem content={streamingContent} role="assistant" /> : null
        }
        contentContainerStyle={{ paddingBottom: 20 }}
      />
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          value={inputText}
          onChangeText={setInputText}
          placeholder="Type a message..."
        />
        <TouchableOpacity onPress={handleSend} style={styles.sendButton}>
          <Text style={styles.sendButtonText}>Send</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  messageBubble: { padding: 10, margin: 5, borderRadius: 10, maxWidth: '80%' },
  userBubble: { alignSelf: 'flex-end', backgroundColor: '#007AFF' },
  assistantBubble: { alignSelf: 'flex-start', backgroundColor: '#E5E5EA' },
  messageText: { color: '#000', fontSize: 16 },
  userMessageText: { color: '#fff' },
  inputContainer: { flexDirection: 'row', padding: 10, borderTopWidth: 1, borderColor: '#ccc', backgroundColor: '#fff' },
  input: { flex: 1, borderWidth: 1, borderColor: '#ccc', borderRadius: 20, paddingHorizontal: 15, paddingVertical: 8, marginRight: 10, backgroundColor: '#fff', fontSize: 16 },
  sendButton: { justifyContent: 'center', paddingHorizontal: 15 },
  sendButtonText: { color: '#007AFF', fontWeight: 'bold', fontSize: 16 },
});
