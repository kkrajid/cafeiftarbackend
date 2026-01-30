import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.urls import get_resolver

def extract_urls(resolver, prefix=''):
    urls = []
    for pattern in resolver.url_patterns:
        if hasattr(pattern, 'url_patterns'):
            urls.extend(extract_urls(pattern, prefix + str(pattern.pattern)))
        else:
            urls.append(prefix + str(pattern.pattern))
    return urls

resolver = get_resolver()
all_urls = extract_urls(resolver)

print("=" * 60)
print("ALL API ENDPOINTS")
print("=" * 60)
for url in sorted(all_urls):
    if url.startswith('api/'):
        print(f"  /{url}")
