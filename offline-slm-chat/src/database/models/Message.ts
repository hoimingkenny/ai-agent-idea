import { Model } from '@nozbe/watermelondb'
import { field, date, relation } from '@nozbe/watermelondb/decorators'
import Conversation from './Conversation'

export default class Message extends Model {
  static table = 'messages'

  @relation('conversations', 'conversation_id') conversation!: any
  
  @field('content') content!: string
  @field('role') role!: 'user' | 'assistant'
  @field('is_embedded') isEmbedded!: boolean
  @date('created_at') createdAt!: Date
}
