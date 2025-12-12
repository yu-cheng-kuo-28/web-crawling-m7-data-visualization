#!/usr/bin/env python3
import re

content = open('nasdaq_goog_page.html', 'r', encoding='utf-8').read()
apis = re.findall(r'["\']([/]api/[^"\']+)["\']', content)
print('Found API endpoints:')
for api in sorted(set(apis))[:30]:
    print(f'  {api}')
