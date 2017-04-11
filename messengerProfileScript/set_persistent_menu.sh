curl -X POST -H "Content-Type: application/json" -d '{
  "setting_type" : "call_to_actions",
  "thread_state" : "existing_thread",
  "call_to_actions":[
    {
      "title":"Record expenses",
      "type":"postback",
      "payload": "PAYLOAD_MENU_TRANSACTION"
    },
    {
      "title":"Record income",
      "type":"postback",
      "payload": "PAYLOAD_MENU_SAVINGS"
    },
    {
      "title":"Show summary",
      "type":"postback",
      "payload": "PAYLOAD_MENU_SUMMARY"
    },
    {
      "title":"Set savings goal",
      "type":"postback",
      "payload": "PAYLOAD_MENU_GOALS"
    }
  ]
}' "https://graph.facebook.com/v2.6/me/thread_settings?access_token=$1"
