import os, sys, httpx

# Bypass Windows system proxy for urllib3 as well
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
os.environ['NO_PROXY'] = '*'

key = os.environ.get('MINIMAX_API_KEY', '')
print('Key len:', len(key))

# Method 1: httpx directly
try:
    client = httpx.Client(proxy=None)
    resp = client.post(
        'https://api.minimaxi.com/v1/chat/completions',
        headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'},
        json={'model': 'MiniMax-M2.7', 'messages': [{'role': 'user', 'content': 'say hi'}]},
        timeout=30
    )
    print('Method 1 httpx direct - Status:', resp.status_code)
except Exception as e:
    print('Method 1 FAIL:', e)

# Method 2: OpenAI SDK with httpx client
try:
    from openai import OpenAI
    http_client = httpx.Client(proxy=None)
    client = OpenAI(api_key=key, base_url='https://api.minimaxi.com/v1', http_client=http_client)
    resp = client.chat.completions.create(
        model='MiniMax-M2.7',
        messages=[{'role': 'user', 'content': 'say hi'}],
        max_tokens=10
    )
    print('Method 2 OpenAI SDK - Success:', resp.choices[0].message.content[:50] if resp.choices else 'no response')
except Exception as e:
    print('Method 2 FAIL:', e)

print('DONE')
