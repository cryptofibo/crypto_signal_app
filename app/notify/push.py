
# Stub-Implementierung für Push: hier würdest du FCM oder OneSignal ansprechen.
def send_push(provider: str, api_key: str, title: str, body: str, topic: str='signals'):
    print(f'[PUSH:{provider}] {title}: {body}')
