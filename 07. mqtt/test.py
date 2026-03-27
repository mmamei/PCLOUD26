




import websocket
import json
import hmac
import hashlib

TOKEN = "f596648e326f9bd625a1d951a42f371e2a097c6b0d52059d"



import websocket
import json



ws = websocket.create_connection("ws://127.0.0.1:18789")

# 1. challenge
msg = json.loads(ws.recv())
print("RECV:", msg)

nonce = msg["payload"]["nonce"]

# 2. session init (QUESTO TI MANCAVA)
init_msg = {
    "type": "session.init",
    "payload": {
        "agentId": "main"
    }
}
ws.send(json.dumps(init_msg))

# 3. authenticate
auth_msg = {
    "type": "connect.authenticate",
    "payload": {
        "auth": {
            "token": TOKEN
        },
        "nonce": nonce
    }
}
ws.send(json.dumps(auth_msg))

# 4. risposta auth
print("AUTH:", ws.recv())

# 5. tool call
send_msg = {
    "type": "tool_call",
    "tool": "sessions_send",
    "args": {
        "session": "agent:main:whatsapp:direct:+393347175155",
        "content": {
            "type": "text",
            "text": "ciao"
        }
    }
}

ws.send(json.dumps(send_msg))

print("RESULT:", ws.recv())

ws.close()