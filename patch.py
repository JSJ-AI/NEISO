import re, sys
with open('index.html', encoding='utf-8') as f:
    c = f.read()
print('Original size:', len(c))
# Remove arc layers
c = c.replace("map.addLayer({id:'ext-flow-line',type:'line',source:'ext-flows',paint:{'line-color':'#1a73e8','line-width':['interpolate',['linear'],['get','mwAbs'],0,2,2000,7],'line-opacity':0.9}});", "// ext-flow removed")
c = c.replace("map.addLayer({id:'zone-flow-line',type:'line',source:'zone-flows',paint:{'line-color':['get','lineColor'],'line-width':['interpolate',['linear'],['get','strength'],0,1.5,60,5],'line-opacity':0.8,'line-dasharray':[4,2]}});", "// zone-flow removed")
c = c.replace("  map.on('mousemove','ext-flow-line',e=>{", "  if(false) map.on('xa',e=>{")
c = c.replace("  map.on('mouseleave','ext-flow-line',()=>{hideTip();map.getCanvas().style.cursor='';});", "")
c = c.replace("  map.on('mousemove','zone-flow-line',e=>{", "  if(false) map.on('xb',e=>{")
c = c.replace("  map.on('mouseleave','zone-flow-line',()=>{hideTip();map.getCanvas().style.cursor='';});", "")
print('arcs removed:', "ext-flow-line" not in c)
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('Done, new size:', len(c))
