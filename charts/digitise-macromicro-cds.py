import json, sys, datetime as dt
from PIL import Image
import numpy as np
P="/root/.claude/uploads/63be7e93-2818-565d-8427-55f1acd09606/"
# name: (file, y_pixel_of_top_grid, top_value, y_pixel_of_zero, [(x_pixel, year)...])
C={
 "France":("c5fc2a8d",239,150,765,[(428.5,2022),(684.5,2024),(940.5,2026)]),
 "United States":("2df96fc8",238,150,764,[(287.5,2010),(512.5,2015),(737.5,2020),(962.5,2025)]),
 "United Kingdom":("a92a7d2b",247,60,773,[(301.5,2015),(614,2020),(929,2025)]),
 "Germany":("1a50783c",240,40,766,[(417.5,2022),(676,2024),(937.5,2026)]),
}
def yr(x,t):  # pixel -> fractional year, linear fit through ticks
    xs=[p for p,_ in t]; ys=[y for _,y in t]
    k,b=np.polyfit(xs,ys,1); return k*x+b
def frac2date(f):
    y=int(f); return dt.date(y,1,1)+dt.timedelta(days=(f-y)*(366 if y%4==0 else 365))
def date2frac(d):
    y=d.year; return y+(d-dt.date(y,1,1)).days/(366 if y%4==0 else 365)
out={}
end=dt.date(2026,10,22); start=end-dt.timedelta(days=365)
for n,(f,ytop,vtop,y0,t) in C.items():
    a=np.array(Image.open(P+f+"-image.jpg").convert("RGB")).astype(int)
    m=(abs(a[:,:,0]-65)<45)&(abs(a[:,:,1]-170)<45)&(abs(a[:,:,2]-210)<45)
    m[:ytop-8]=False; m[y0+4:]=False; m[:,:178]=False
    xs=np.nonzero(m.any(axis=0))[0]; xmax=xs.max()
    k,b=np.polyfit([y for _,y in t],[p for p,_ in t],1)
    b=xmax-k*date2frac(end)  # anchor: last drawn pixel = 22 Oct 2026; scale from year ticks
    print(n,'px/yr',round(k,1))
    # anchor the last drawn pixel to Oct 22 2026 by shifting the date axis only if close
    def val(x0):
        cols=[int(round(x0))]
        ys=np.concatenate([np.nonzero(m[:,c])[0] for c in cols if 0<=c<m.shape[1]])
        if len(ys)==0: return None
        # steep sections: use midpoint of extent when thick, else mean
        yy=ys.mean()
        return (y0-yy)/(y0-ytop)*vtop
    rows=[]
    d=start
    while d<=end-dt.timedelta(days=2):
        x=k*date2frac(d)+b
        if x<=xmax+1:
            v=val(min(x,xmax))
            if v is not None: rows.append([d.isoformat(),round(v,1)])
        d+=dt.timedelta(days=3)
    # always include the last observation (22 Oct) at the final drawn column
    v=val(xmax); rows.append([end.isoformat(),round(v,1)])
    out[n]=rows
json.dump(out,open("/tmp/claude-0/-home-user-Claude-Scratch/63be7e93-2818-565d-8427-55f1acd09606/scratchpad/cds.json","w"))
for n,r in out.items(): print(n,len(r),r[0],r[len(r)//2],r[-3:])
