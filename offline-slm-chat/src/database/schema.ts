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
