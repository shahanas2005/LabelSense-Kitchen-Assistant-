import requests
import json

checks = {
    'backend_openapi': 'http://localhost:8000/openapi.json',
    'analyze_post_sample': 'http://localhost:8000/api/analyze',
    'frontend_5174': 'http://localhost:5174/',
    'frontend_5173': 'http://localhost:5173/'
}
results = {}

for name, url in checks.items():
    try:
        if name == 'analyze_post_sample':
            # POST sample image if available
            import os
            p = os.path.join('data', 'sample-label-clear.png')
            if os.path.exists(p):
                with open(p, 'rb') as f:
                    files = {'image': ('sample-label-clear.png', f, 'image/png')}
                    r = requests.post(url, files=files, data={'user_id':'1'}, timeout=10)
                    results[name] = r.status_code
                    try:
                        results[name+'_json'] = r.json()
                    except Exception as e:
                        results[name+'_json'] = str(e)
            else:
                results[name] = 'sample image missing'
        else:
            r = requests.get(url, timeout=5)
            results[name] = r.status_code
    except Exception as e:
        results[name] = str(e)

print(json.dumps(results, indent=2))
