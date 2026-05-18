import urllib.request

urls = [
    'http://127.0.0.1:8000/health',
    'http://127.0.0.1:8000/genes',
]
for url in urls:
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            print(url, r.status)
            print(r.read().decode('utf-8', errors='replace'))
    except Exception as e:
        print(url, 'ERROR', e)
