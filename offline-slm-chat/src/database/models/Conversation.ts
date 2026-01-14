import { Model } from '@nozbe/watermelondb'
import { field, children, date } from '@nozbe/watermelondb/decorators'

export default class Conversation extends Model {
  static table = 'conversations'

  @field('title') title!: string
  @field('archived') archived!: boolean
  @date('created_at') createdAt!: Date
  
  @children('messages') messages!: any
}
