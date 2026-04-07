with open('index.html', encoding='utf-8') as f:
    c = f.read()
print('Size:', len(c))
si = c.find('function renderSchematic(){')
ei = c.find('function renderCharts(){')
print('si:', si, 'ei:', ei)
if si == -1 or ei == -1:
    print('ERROR: markers not found'); exit(1)
new_fn = open('schematic_fn.js', encoding='utf-8').read()
c = c[:si] + new_fn + c[ei:]
print('New size:', len(c))
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('Done')
