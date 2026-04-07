import re

with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

print(f"Original size: {len(c)}")

# 1. Remove blue arc layers from map
c = c.replace(
    "map.addLayer({id:'ext-flow-line',type:'line',source:'ext-flows',paint:{'line-color':'#1a73e8','line-width':['interpolate',['linear'],['get','mwAbs'],0,2,2000,7],'line-opacity':0.9}});",
    "// ext-flow-line removed - flows shown on Schematic tab"
)
c = c.replace(
    "map.addLayer({id:'zone-flow-line',type:'line',source:'zone-flows',paint:{'line-color':['get','lineColor'],'line-width':['interpolate',['linear'],['get','strength'],0,1.5,60,5],'line-opacity':0.8,'line-dasharray':[4,2]}});",
    "// zone-flow-line removed - flows shown on Schematic tab"
)
c = c.replace(
    "  map.on('mousemove','ext-flow-line',e=>{",
    "  if(false) map.on('mousemove','ext-flow-line-off',e=>{"
)
c = c.replace(
    "  map.on('mouseleave','ext-flow-line',()=>{hideTip();map.getCanvas().style.cursor='';});",
    ""
)
c = c.replace(
    "  map.on('mousemove','zone-flow-line',e=>{",
    "  if(false) map.on('mousemove','zone-flow-line-off',e=>{"
)
c = c.replace(
    "  map.on('mouseleave','zone-flow-line',()=>{hideTip();map.getCanvas().style.cursor='';});",
    ""
)
c = c.replace(
    '<button class="map-ctrl-btn active" id="btn-flows" onclick="toggleFlows()">Flow arrows</button>',
    ''
)
print(f"Arc layers removed: {\"id:'ext-flow-line'\" not in c and \"id:'zone-flow-line'\" not in c}")

# 2. Replace renderSchematic function
NEW_SCHEMATIC = r"""function renderSchematic(){
  const svg=document.getElementById('schematic-svg');
  svg.setAttribute('viewBox','0 0 820 570');
  svg.innerHTML='';
  const NS='http://www.w3.org/2000/svg';
  function el(tag,attrs,txt){const e=document.createElementNS(NS,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v));if(txt!==undefined)e.textContent=txt;return e;}
  function ap(p,...ch){ch.forEach(c=>p.appendChild(c));return p;}
  const FC={'Natural Gas':'#f4511e','Nuclear':'#8e24aa','Hydro':'#1a73e8','Wind':'#43a047','Solar':'#f9a825','Oil':'#795548','Other':'#90a4ae','Wood':'#6d4c41','Refuse':'#546e7a','Landfill Gas':'#00acc1','Coal':'#616161'};
  const ZP={ME:{x:600,y:55,w:170,h:115},NH:{x:420,y:60,w:158,h:110},VT:{x:240,y:55,w:158,h:110},WCMA:{x:240,y:225,w:168,h:118},NEMA:{x:420,y:225,w:158,h:118},SEMA:{x:598,y:225,w:170,h:118},CT:{x:80,y:400,w:175,h:120},RI:{x:440,y:400,w:158,h:120}};
  ap(svg,el('rect',{x:0,y:0,width:820,height:570,fill:'#f8f9fa'}));
  const tot=state.fuelMix.reduce((s,f)=>s+(f.GenMw||0),0);
  const ftop=state.fuelMix.filter(f=>(f.GenMw||0)>30).sort((a,b)=>b.GenMw-a.GenMw).slice(0,7);
  ap(svg,el('text',{x:12,y:11,'font-size':'9','font-family':'Inter,sans-serif','font-weight':'600',fill:'#888'},'Generation mix'));
  let bx=12;
  ftop.forEach(f=>{const fw=Math.round((f.GenMw||0)/tot*200);const fc=FC[f.FuelCategory||f.FuelCategoryRollup]||'#90a4ae';ap(svg,el('rect',{x:bx,y:14,width:fw,height:11,fill:fc,rx:1}));bx+=fw;});
  let lx=12;
  ftop.slice(0,6).forEach(f=>{const fc=FC[f.FuelCategory||f.FuelCategoryRollup]||'#90a4ae';const pct=Math.round((f.GenMw||0)/tot*100);ap(svg,el('rect',{x:lx,y:28,width:7,height:7,fill:fc,rx:1}),el('text',{x:lx+9,y:35,'font-size':'8.5','font-family':'Inter,sans-serif',fill:'#666'},(f.FuelCategory||f.FuelCategoryRollup||'?').substring(0,9)+' '+pct+'%'));lx+=70;});
  const sl=state.sysload;
  if(sl){const net=Math.round(state.flows.reduce((s,f)=>s+(f.flow||0),0));const solar=Math.round((sl.SystemLoadBtmPv||0)-(sl.LoadMw||0));[['System load',Math.round(sl.LoadMw||0).toLocaleString()+' MW'],['Solar BTM',solar.toLocaleString()+' MW'],['Net interchange',(net>=0?'+':'')+net+' MW']].forEach(([lb,vl],i)=>{ap(svg,el('text',{x:808,y:11+i*13,'text-anchor':'end','font-size':'9','font-family':'Inter,sans-serif','font-weight':'500',fill:'#888'},lb),el('text',{x:808,y:11+i*13,'text-anchor':'start','font-size':'9','font-family':'JetBrains Mono,monospace','font-weight':'700',fill:'#333',dx:'4'},vl));});}
  function lmpC(v){if(v===null)return{fill:'#eceff1',border:'#90a4ae',text:'#546e7a',hdr:'#90a4ae'};if(v<0)return{fill:'#f3e5f5',border:'#7b1fa2',text:'#6a1b9a',hdr:'#7b1fa2'};if(v<30)return{fill:'#e8f5e9',border:'#43a047',text:'#2e7d32',hdr:'#43a047'};if(v<60)return{fill:'#fff3e0',border:'#fb8c00',text:'#e65100',hdr:'#fb8c00'};if(v<90)return{fill:'#ffebee',border:'#e53935',text:'#c62828',hdr:'#e53935'};return{fill:'#fce4ec',border:'#880e4f',text:'#880e4f',hdr:'#880e4f'};}
  function drawZone(zid){
    const pos=ZP[zid];if(!pos)return;
    const zs=Object.values(state.zones).find(z=>z.zoneId===zid);
    const lmp=zs?zs.lmp:null;const {fill,border,text,hdr}=lmpC(lmp);const g=el('g',{});
    ap(g,el('rect',{x:pos.x+2,y:pos.y+2,width:pos.w,height:pos.h,fill:'rgba(0,0,0,0.07)',rx:8}));
    ap(g,el('rect',{x:pos.x,y:pos.y,width:pos.w,height:pos.h,fill,stroke:border,'stroke-width':2,rx:8}));
    ap(g,el('rect',{x:pos.x,y:pos.y,width:pos.w,height:24,fill:hdr,rx:8}));
    ap(g,el('rect',{x:pos.x,y:pos.y+16,width:pos.w,height:8,fill:hdr}));
    ap(g,el('text',{x:pos.x+pos.w/2,y:pos.y+16,'text-anchor':'middle','font-size':'11','font-family':'Inter,sans-serif','font-weight':'700',fill:'#fff'},zid));
    ap(g,el('text',{x:pos.x+pos.w/2,y:pos.y+44,'text-anchor':'middle','font-size':'17','font-family':'JetBrains Mono,monospace','font-weight':'700',fill:text},lmp!==null?'$'+lmp.toFixed(2):'-'));
    ap(g,el('text',{x:pos.x+pos.w/2,y:pos.y+54,'text-anchor':'middle','font-size':'8','font-family':'Inter,sans-serif',fill:'#aaa'},'$/MWh LMP'));
    ap(g,el('line',{x1:pos.x+10,y1:pos.y+60,x2:pos.x+pos.w-10,y2:pos.y+60,stroke:'rgba(0,0,0,0.1)','stroke-width':'0.5'}));
    if(zs&&zs.load!=null){ap(g,el('text',{x:pos.x+10,y:pos.y+71,'font-size':'8','font-family':'Inter,sans-serif','font-weight':'600',fill:'#777'},'LOAD'),el('text',{x:pos.x+10,y:pos.y+82,'font-size':'10','font-family':'JetBrains Mono,monospace','font-weight':'600',fill:'#333'},Math.round(zs.load).toLocaleString()+' MW'));}
    if(zs&&zs.btm!=null&&zs.btm>0){ap(g,el('text',{x:pos.x+pos.w-10,y:pos.y+71,'text-anchor':'end','font-size':'8','font-family':'Inter,sans-serif','font-weight':'600',fill:'#777'},'BTM \u2600'),el('text',{x:pos.x+pos.w-10,y:pos.y+82,'text-anchor':'end','font-size':'10','font-family':'JetBrains Mono,monospace','font-weight':'600',fill:'#43a047'},Math.round(zs.btm).toLocaleString()+' MW'));}
    if(zs&&zs.energy!=null){const bw=pos.w-20,bh=6,by2=pos.y+pos.h-14,bxz=pos.x+10;const epx=Math.max(Math.min((zs.energy||0)/40,1)*bw,2);const cpx=Math.min(Math.abs(zs.cong||0)/5,1)*(bw*0.25);ap(g,el('rect',{x:bxz,y:by2,width:bw,height:bh,fill:'rgba(0,0,0,0.07)',rx:2}),el('rect',{x:bxz,y:by2,width:epx,height:bh,fill:'#1a73e8',rx:2}));if(Math.abs(zs.cong||0)>0.1)ap(g,el('rect',{x:bxz+epx,y:by2,width:Math.max(cpx,1.5),height:bh,fill:(zs.cong||0)>0?'#e53935':'#7b1fa2',rx:1}));ap(g,el('text',{x:bxz,y:by2-2,'font-size':'7.5','font-family':'Inter,sans-serif',fill:'#aaa'},'E:$'+(zs.energy||0).toFixed(1)+(Math.abs(zs.cong||0)>0.1?' C:$'+(zs.cong||0).toFixed(1):'')));}
    ap(svg,g);
  }
  function drawZoneFlow(fId,tId,ox){
    const fp=ZP[fId],tp=ZP[tId];if(!fp||!tp)return;
    const zsF=Object.values(state.zones).find(z=>z.zoneId===fId);
    const zsT=Object.values(state.zones).find(z=>z.zoneId===tId);
    if(!zsF||!zsT||zsF.lmp===null||zsT.lmp===null)return;
    const diff=zsT.lmp-zsF.lmp;if(Math.abs(diff)<0.05)return;
    const sP=diff>0?fp:tp,dP=diff>0?tp:fp;
    const sr=Math.abs(sP.y-dP.y)<60;
    let x1,y1,x2,y2;
    if(sr){const gr=dP.x>sP.x;x1=gr?sP.x+sP.w:sP.x;y1=sP.y+sP.h/2;x2=gr?dP.x:dP.x+dP.w;y2=dP.y+dP.h/2;}
    else{x1=sP.x+sP.w/2+(ox||0);y1=dP.y>sP.y?sP.y+sP.h:sP.y;x2=dP.x+dP.w/2+(ox||0);y2=dP.y>sP.y?dP.y:dP.y+dP.h;}
    const ad=Math.abs(diff);const col=ad>20?'#e53935':ad>8?'#fb8c00':ad>3?'#1a73e8':'#90a4ae';
    const sw=Math.max(1.2,Math.min(ad/3,3.5));
    const mx=(x1+x2)/2,my=(y1+y2)/2;
    const ang=Math.atan2(y2-y1,x2-x1);const al=9,aw=4.5;
    const ax1=x2-al*Math.cos(ang)+aw*Math.sin(ang),ay1=y2-al*Math.sin(ang)-aw*Math.cos(ang);
    const ax2=x2-al*Math.cos(ang)-aw*Math.sin(ang),ay2=y2-al*Math.sin(ang)+aw*Math.cos(ang);
    ap(svg,el('line',{x1,y1,x2,y2,stroke:col,'stroke-width':sw,opacity:'0.8'}),el('polygon',{points:x2+','+y2+' '+ax1+','+ay1+' '+ax2+','+ay2,fill:col,opacity:'0.9'}),el('rect',{x:mx-18,y:my-7,width:36,height:13,fill:'rgba(255,255,255,0.88)',rx:3}),el('text',{x:mx,y:my+2,'text-anchor':'middle','font-size':'8','font-family':'JetBrains Mono,monospace','font-weight':'700',fill:col},'\u0394$'+ad.toFixed(2)));
  }
  function drawExtFlow(key,label,ex,ey,toZid,side){
    const flow=state.flows.find(f=>f.name.toUpperCase().includes(key.toUpperCase()));
    if(!flow||Math.abs(flow.flow)<5)return;
    const mw=Math.abs(Math.round(flow.flow));const imp=flow.flow<0;
    const tp=ZP[toZid];if(!tp)return;
    let tx,ty;
    if(side==='left'){tx=tp.x;ty=tp.y+tp.h/2;}else if(side==='right'){tx=tp.x+tp.w;ty=tp.y+tp.h/2;}else if(side==='top'){tx=tp.x+tp.w/2;ty=tp.y;}else{tx=tp.x+tp.w/2;ty=tp.y+tp.h;}
    const x1=imp?ex:tx,y1=imp?ey:ty,x2=imp?tx:ex,y2=imp?ty:ey;
    const col=imp?'#0d47a1':'#b71c1c';const sw=Math.min(2+mw/300,5.5);
    const ang=Math.atan2(y2-y1,x2-x1);const al=10,aw=5;
    const ax1=x2-al*Math.cos(ang)+aw*Math.sin(ang),ay1=y2-al*Math.sin(ang)-aw*Math.cos(ang);
    const ax2=x2-al*Math.cos(ang)-aw*Math.sin(ang),ay2=y2-al*Math.sin(ang)+aw*Math.cos(ang);
    const mx=(x1+x2)/2,my=(y1+y2)/2;
    ap(svg,el('line',{x1,y1,x2,y2,stroke:col,'stroke-width':sw,opacity:'0.9'}),el('polygon',{points:x2+','+y2+' '+ax1+','+ay1+' '+ax2+','+ay2,fill:col}),el('rect',{x:mx-28,y:my-8,width:56,height:14,fill:'rgba(255,255,255,0.9)',rx:3,stroke:col,'stroke-width':'0.5'}),el('text',{x:mx,y:my+2,'text-anchor':'middle','font-size':'8.5','font-family':'JetBrains Mono,monospace','font-weight':'700',fill:col},label+' '+(imp?'\u2193':'\u2191')+mw+'MW'));
  }
  drawZoneFlow('VT','WCMA');drawZoneFlow('NH','NEMA');drawZoneFlow('ME','NH',-20);
  drawZoneFlow('WCMA','NEMA');drawZoneFlow('NEMA','SEMA');drawZoneFlow('NEMA','CT',20);
  drawZoneFlow('SEMA','RI');drawZoneFlow('CT','RI');
  drawExtFlow('ROSETON','NY-H',10,ZP.WCMA.y+ZP.WCMA.h/2,'WCMA','left');
  drawExtFlow('SALBRYNB','NY-N',10,ZP.CT.y+ZP.CT.h/2,'CT','left');
  drawExtFlow('HQMRL','QC-NE',ZP.ME.x+ZP.ME.w/2,10,'ME','top');
  drawExtFlow('HQ_P1','QC-P1',ZP.VT.x+ZP.VT.w/2,10,'VT','top');
  drawExtFlow('HQHIGATE','NB',810,ZP.ME.y+30,'ME','right');
  Object.keys(ZP).forEach(drawZone);
  const ts=Object.values(state.zones).find(z=>z.ts)?new Date(Object.values(state.zones).find(z=>z.ts).ts).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'}):'--:--';
  ap(svg,el('text',{x:410,y:563,'text-anchor':'middle','font-size':'8.5','font-family':'Inter,sans-serif',fill:'#ccc'},'ISO-NE Load Zones \u00b7 LMP $/MWh \u00b7 '+ts+' \u00b7 Arrow=energy flow \u00b7 \u0394$=price spread \u00b7 \u2193=import \u2191=export'));
}

"""

si = c.find('function renderSchematic(){')
ei = c.find('function renderCharts(){')
print(f"renderSchematic at {si}, renderCharts at {ei}")
if si == -1 or ei == -1:
    print("ERROR: markers not found")
    exit(1)

c = c[:si] + NEW_SCHEMATIC + c[ei:]
print(f"New size: {len(c)}")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("Written successfully")
