import json

tags = json.load(open('tags.json'))

print '''<?xml version="1.0" encoding="utf-8"?>
<DMX_CONTROL version="2.00">'''

print '''  <event type="NORMAL_CONDITION_1" continuous="yes">
    <timeblock mseconds="500">'''
for i in range(len(tags)):
    print '      <setvalue index="%d" value="0" change="0"/>' % i
print '''    </timeblock>
  </event>'''

for i, a in enumerate(tags):
    tag = a[0]
    continuous = 'yes' if a[1] == 'level' else 'no'
    print '''  <event type="%s" continuous="%s">
    <timeblock mseconds="100">
      <setvalue index="%d" value="255" change="0"/>
    </timeblock>
  </event>''' % (tag, continuous, i)

print '</DMX_CONTROL>'
