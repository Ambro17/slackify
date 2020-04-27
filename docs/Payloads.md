# User Interactions
 - Shortcuts
 - Commands
 - Interactive Components

## Decorators
```
app.command(commandName, fn);
app.shortcut(callbackId, fn);
app.action(actionId, fn);
app.view(callbackId, fn);

app.event(eventType, fn);
```


## Shortcuts
 [API Docs](https://api.slack.com/reference/interaction-payloads/shortcuts)
 - Global
 - Message

### Payloads
`Content-Type: application/json`

`payload = request.get_json()['payload']`

#### Global Shortcut
```json
{
  "type": "shortcut",
  "callback_id": "shortcut_create_task",
  "trigger_id": "944799105734.773906753841"
  "token": "secret-123",
  "action_ts": "1581106241.371594",
  "team": {
    "id": "TXXXXXXXX",
    "domain": "shortcuts-test"
  },
  "user": {
    "id": "UXXXXXXXXX",
    "username": "aman",
    "team_id": "TXXXXXXXX"
  }
}
```
#### Message Shortcut
```json
{
  "type": "message_action",
  "callback_id": "message-shortcut-id",
  "trigger_id": "13345224609.8534564800",
  "token": "secret-123",
  "response_url": "https://hooks.slack.com/url",
  "team": {
    "id": "T0MJRM1A7",
    "domain": "pandamonium",
  },
  "channel": {
    "id": "D0LFFBKLZ",
    "name": "cats"
  },
  "user": {
    "id": "U0D15K92L",
    "name": "dr_maomao"
  },
  "message": {
    "type": "message",
    "user": "U0MJRG1AL",
    "ts": "1516229207.000133",
    "text": "Some Random Text"
  }
}
```
Almost the same but. type value changes and channel, message and response_url are added.


## Commands
[API Docs](https://api.slack.com/interactivity/slash-commands#app_command_handling)
`Content-Type: application/x-www-form-urlencoded`

`payload = request.form`
The response is not json as if is form-encoded. But for documentation purposes, it is ok to show it as json as it is more readable:
```
command=/repeat
text=command%20arguments
user_id=U1234
user_name=Steve
channel_id=C1234
channel_name=test
response_url=https://hooks.slack.com/commands/url
token=token
team_id=T0001
team_domain=my_company
enterprise_id=E0001
enterprise_name=EvilInc
```

## Interactive Components
Slack has a special endpoint for triggers triggered when user interacts with a `Block Kit Element`. That may be a button, a dropdown, a datepicker. etc. [Learn more](https://api.slack.com/reference/block-kit/block-elements)
There are different types that differ on the sent payload
- Block Actions
- View Submission & Closed
- Shortcuts (Already covered)

### Payload
They all have the same request signature.
```
POST
Content-Type: application/x-www-form-urlencoded
action = json.loads(request.form["payload"])
```
Why they encode json into a form payload? We might never know..

#### Types
- `block_actions`  On user interaction in block element.
- `message_actions` (Already covered as message shortcuts)
- `view_submission` On open modal
- `view_closed`   On closed modal

#### `block_actions` Payload
[Source](https://github.com/slackapi/bolt/blob/master/src/types/actions/block-action.ts)
```json
{
  type: 'block_actions';
  actions: [ElementAction];
  team: {id domain}
  user: {id name team_id}
  channel?: { id name } // present if action is triggered from message. a.k.a message_action
  message?: {  // present if action is triggered from message. a.k.a message_action
    type: 'message';
    ts: string;
  };
  view?: ViewOutput;
  token: string;
  response_url: string;
  trigger_id: string;
  api_app_id: string;
  container: StringIndexed;
  app_unfurl?: any;
}
```
where `ElementAction` is an interface implemented and extended by each block element.
```
{
  block_id: string;
  action_id: string;
  action_ts: string;
}
```
`callback_id` depends on the element. See this pseudocode to understand it.
```
    if isViewBody(body):
        callbackId = body['view']['callback_id'];
    elif isCallbackIdentifiedBody(body) {
        callbackId = body['callback_id'];
    }

type CallbackIdentifiedBody =
  | InteractiveMessage
  | DialogSubmitAction
  | MessageShortcut
  | GlobalShortcut
  | OptionsRequest<'interactive_message' | 'dialog_suggestion'>;
```

For example a `selected_option` element
```
{
  selected_option: {
    text: PlainTextElement,
    value: string;
  };
  initial_option?: Option;
  placeholder?: PlainTextElement;
  confirm?: Confirmation;
}
```
