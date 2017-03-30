curl -X POST -H "Content-Type: application/json" -d '{
  "persistent_menu":[
    {
      "locale":"default",
      "composer_input_disabled":true,
      "call_to_actions":[
        {
          "title":"Add a transaction",
          "type":"nested",
          "call_to_actions":[
            {
              "title":"Breakfast",
              "type":"postback",
              "payload":"BREAKFAST_PAYLOAD"
            },
            {
              "title":"Groceries",
              "type":"postback",
              "payload":"GROCERIES_PAYLOAD"
            },
            {
              "title":"Transport",
              "type":"postback",
              "payload":"TRANSPORT_PAYLOAD"
            }
          ]
        },
        {
          "type":"postback",
          "title":"Set a savings goal",
          "payload": "SAVINGS_PAYLOAD"
        }
      ]
    },
    {
      "locale":"en_US",
      "composer_input_disabled":false
    }
  ]
}' "https://graph.facebook.com/v2.6/me/messenger_profile?access_token=$1"
