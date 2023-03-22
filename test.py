import re

html_string = """
<div>
  <ul>
    <li>Bobby</li>
    <li>Hadz</li>
    <li>Com</li>
  </ul>
</div>
"""

pattern = re.compile('<.*?>')


result = re.sub(pattern, '', html_string)

# Bobby
# Hadz
# Com

print(result)