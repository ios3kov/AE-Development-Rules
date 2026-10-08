#!/usr/bin/env python3
"""Compare exported RGBA buffers and extract observed UI tokens; no rescaling."""
import argparse
import json
import math
from pathlib import Path
import sys
from check_reference_obligations import load_json, text
from reference_engineering import require

MATCH = ("width","height","bit_depth","color_space","alpha_mode","device","viewport","scale","font_identity","render_path")

def compare(data):
    require(isinstance(data,dict),"comparison must be object")
    a,b=data.get("reference"),data.get("candidate")
    require(isinstance(a,dict) and isinstance(b,dict),"matched captures required")
    require(all(k in a and a[k]==b.get(k) for k in MATCH),"capture environment/format mismatch")
    require(type(a["width"]) is int and type(a["height"]) is int and a["width"]>0 and a["height"]>0,"positive image dimensions required")
    require(a["bit_depth"] in (8,16,32) and a["alpha_mode"] in ("straight","premultiplied"),"explicit RGBA format required")
    for k in ("color_space","device","font_identity","render_path"):
        require(text(a[k]),"capture metadata incomplete")
    require(type(a["scale"]) in (int,float) and math.isfinite(a["scale"]) and a["scale"]>0, "positive capture scale required")
    require(isinstance(a["viewport"],list) and len(a["viewport"])==2 and all(type(v) is int and v>0 for v in a["viewport"]), "positive viewport dimensions required")
    size=a["width"]*a["height"]*4
    for image in (a,b):
        pixels=image.get("rgba")
        require(isinstance(pixels,list) and len(pixels)==size,"full RGBA buffer required")
        require(all(type(x) in (int,float) and math.isfinite(x) for x in pixels),"invalid pixel")
        if a["bit_depth"]!=32:
            limit=2**a["bit_depth"]-1
            require(all(type(x) is int and 0<=x<=limit for x in pixels),"invalid integer channel")
    tolerance=data.get("tolerance",0)
    require(type(tolerance) in (int,float) and math.isfinite(tolerance) and tolerance>=0,"reviewed nonnegative tolerance required")
    regions=data.get("regions")
    require(isinstance(regions,list) and regions,"named comparison regions required")
    reports=[]
    seen=set()
    for region in regions:
        require(isinstance(region,dict) and text(region.get("id")) and region["id"] not in seen,"unique region ID required")
        seen.add(region["id"])
        values=[region.get(k) for k in ("x","y","width","height")]
        require(all(type(v) is int for v in values),"integer region bounds required")
        x,y,width,height=values
        require(x>=0 and y>=0 and width>0 and height>0 and x+width<=a["width"] and y+height<=a["height"],"region outside capture")
        diffs=[abs(a["rgba"][((row*a["width"]+col)*4)+c]-b["rgba"][((row*a["width"]+col)*4)+c]) for row in range(y,y+height) for col in range(x,x+width) for c in range(4)]
        reports.append({"id":region["id"],"max_channel_difference":max(diffs),"changed_channels":sum(v>tolerance for v in diffs)})
    # Region annotations cannot hide a difference elsewhere.
    total=sum(abs(x-y)>tolerance for x,y in zip(a["rgba"],b["rgba"]))
    return {"status":"FAIL" if total else "PASS","scope":"full-RGBA-comparison","changed_channels":total,"regions":reports,
            "rescaled":False,"alpha_preserved":True,"product_parity_certified":False}

def tokens(data):
    require(isinstance(data,dict) and isinstance(data.get("controls"),list),"observed UI controls required")
    result={"colors":set(),"font_sizes":set(),"spacing":set()}
    for control in data["controls"]:
        require(isinstance(control,dict) and text(control.get("evidence_id")),"token source Evidence required")
        for key in result:
            values=control.get(key,[])
            require(isinstance(values,list),"token values must be arrays")
            for value in values:
                if key=="colors":
                    require(isinstance(value,str) and len(value)==7 and value[0]=='#',"opaque sRGB hex required")
                    int(value[1:],16)
                    result[key].add(value.lower())
                else:
                    require(type(value) in (int,float) and math.isfinite(value) and value>=0,"invalid numeric token")
                    result[key].add(value)
    return {"status":"PASS","scope":"observed-token-extraction","tokens":{k:sorted(v) for k,v in result.items()},"inferred_from_screenshot":False}

def contrast(data):
    def luminance(color):
        require(isinstance(color,str) and len(color)==7 and color[0]=='#',"opaque sRGB colors required")
        values=[int(color[i:i+2],16)/255 for i in (1,3,5)]
        linear=[v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4 for v in values]
        return sum(v*w for v,w in zip(linear,(0.2126,0.7152,0.0722)))
    require(isinstance(data,dict),"contrast input required")
    fg,bg=luminance(data.get("foreground")),luminance(data.get("background"))
    minimum=data.get("minimum_ratio")
    require(type(minimum) in (int,float) and math.isfinite(minimum) and minimum>=1,"scope-specific contrast minimum required")
    ratio=(max(fg,bg)+0.05)/(min(fg,bg)+0.05)
    return {"status":"PASS" if ratio>=minimum else "FAIL","scope":"declared-sRGB-contrast","ratio":ratio,"minimum_ratio":minimum,"accessibility_certified":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("operation",choices=["compare","tokens","contrast"])
    p.add_argument("input",type=Path)
    args=p.parse_args()
    try:
        result={"compare":compare,"tokens":tokens,"contrast":contrast}[args.operation](load_json(args.input))
    except (OSError,ValueError,TypeError,RuntimeError) as exc:
        result={"status":"FAIL","errors":[str(exc)]}
    print(json.dumps(result,allow_nan=False))
    return 0 if result["status"]=="PASS" else 1

if __name__=="__main__":
    sys.exit(main())
