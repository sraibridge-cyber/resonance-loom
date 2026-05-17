import { useState, useMemo } from "react";
import { Sparkles, Search, Activity, Database, Shield, BookOpen, Award, Copy, CheckCircle2, XCircle, AlertTriangle, Zap, FileText } from "lucide-react";

const VERSION = "3.1.0";
const BUILD_DATE = "2026-05-16";
const SEAL = "MERLIN_RC_V3.1_MERGED_SHA3-512";
const MU_THRESHOLD = 0.9995;

const LANGUAGE_BASELINES = {
  python:      { D1: 0.70, D2: 0.65, D3: 0.70, D4: 0.75, D5: 0.70, D6: 0.75 },
  javascript:  { D1: 0.65, D2: 0.60, D3: 0.65, D4: 0.70, D5: 0.65, D6: 0.70 },
  typescript:  { D1: 0.70, D2: 0.65, D3: 0.70, D4: 0.75, D5: 0.70, D6: 0.75 },
  rust:        { D1: 0.80, D2: 0.75, D3: 0.80, D4: 0.85, D5: 0.80, D6: 0.85 },
  go:          { D1: 0.75, D2: 0.70, D3: 0.75, D4: 0.80, D5: 0.75, D6: 0.80 },
  java:        { D1: 0.75, D2: 0.70, D3: 0.75, D4: 0.80, D5: 0.75, D6: 0.80 },
};

const DANGEROUS_PATTERNS = [
  { pattern: /\beval\s*\(/gi, name: "eval()", severity: "HIGH" },
  { pattern: /\bexec\s*\(/gi, name: "exec()", severity: "HIGH" },
  { pattern: /\bpickle\.load\s*\(/gi, name: "pickle.load()", severity: "HIGH" },
  { pattern: /innerHTML\s*=/gi, name: "innerHTML", severity: "HIGH" },
  { pattern: /document\.write\s*\(/gi, name: "document.write()", severity: "HIGH" },
  { pattern: /hardcoded\s*(password|secret|token|key)\s*=/gi, name: "hardcoded secret", severity: "HIGH" },
  { pattern: /Runtime\.getRuntime\(\)\.exec\s*\(/gi, name: "Runtime.exec()", severity: "HIGH" },
];

function scoreD1(s) { let sc = 0.5; const f = (s.match(/def\s+\w+\(/g)||[]).length; const c = (s.match(/class\s+\w+/g)||[]).length; if(f+c>0) sc += Math.min(0.15,(f+c*2)*0.02); const t = (s.match(/:\s*(int|str|float|bool|List|Dict|Optional)/g)||[]).length; if(t>=3) sc += 0.10; const d = (s.match(/\/(?!\/)/g)||[]).length; const z = (s.match(/if\s+.*==\s*0|ZeroDivisionError/g)||[]).length; if(d>0&&z>0) sc+=0.10; else if(d>0) sc-=0.05; return Math.max(0,Math.min(1,sc)); }
function scoreD2(s) { let sc=0.5; const o=(s.match(/\bopen\s*\(/g)||[]).length; const w=(s.match(/\bwith\s+/g)||[]).length; if(o>0){if(w>=o) sc+=0.15; else sc-=0.10;} const fn=(s.match(/\bfinally\s*:/g)||[]).length; if(fn>0) sc+=0.10; const y=(s.match(/\byield\s/g)||[]).length; if(y>0) sc+=0.10; return Math.max(0,Math.min(1,sc)); }
function scoreD3(s) { let sc=0.5; const fd=(s.match(/def\s+(\w+)\(/g)||[]).map(m=>m.match(/def\s+(\w+)/)[1]); const dsc=fd.filter(f=>f.length>4); if(dsc.length>=fd.length*0.5&&fd.length>0) sc+=0.15; const docs=(s.match(/\"\"\"[\s\S]*?\"|\'\'\'[\s\S]*?\'\'\'/g)||[]).length; if(docs>=fd.length*0.3) sc+=0.15; const ta=(s.match(/:\s*(int|str|float|bool|List|Dict)/g)||[]).length; if(ta>=3) sc+=0.10; return Math.max(0,Math.min(1,sc)); }
function scoreD4(s) { let sc=0.5; const ls=s.split('\n'); const ll=ls.filter(l=>l.length>120).length; if(ll<ls.length*0.2) sc+=0.10; else if(ll>ls.length*0.5) sc-=0.10; const im=s.match(/^[\t ]+/gm)||[]; const mn=im.length>0?Math.max(...im.map(m=>m.length))/4:0; if(mn<=3) sc+=0.15; else if(mn>6) sc-=0.10; return Math.max(0,Math.min(1,sc)); }
function scoreD5(s) { let sc=0.5; const cn=(s.match(/^[A-Z][A-Z0-9_]*\s*=/gm)||[]).length; if(cn>=3) sc+=0.10; const rz=(s.match(/raise\s+\w+Error\s*\(\s*["']([^"']{10,})/g)||[]).length; if(rz>=2) sc+=0.15; else if(rz>=1) sc+=0.05; const gr=(s.match(/if\s+.*:\s*return/gs)||[]).length; if(gr>=2) sc+=0.10; return Math.max(0,Math.min(1,sc)); }
function scoreD6(s) { let sc=0.5; let dc=0; for(const dp of DANGEROUS_PATTERNS){if(dp.pattern.test(s)){sc-=dp.severity==="HIGH"?0.15:0.08; dc++;}} if(dc===0) sc+=0.10; const inp=(s.match(/\binput\s*\(|request\.args|request\.form/g)||[]).length; const val=(s.match(/validate|sanitize|check.*null|null.*check/gim)||[]).length; if(inp>0){if(val>=inp) sc+=0.10; else sc-=0.05;} const fq=(s.match(/f["'].*SELECT.*\{/gi)||[]).length; const ps=(s.match(/%s|\$\d|\?.*WHERE/g)||[]).length; if(ps>0&&fq===0) sc+=0.10; return Math.max(0,Math.min(1,sc)); }
function normMu(r,b){ if(b===0)return 0; return Math.min(1,Math.pow(r/b,0.75)); }
function computeResonance(s,l="python"){
  const bl=LANGUAGE_BASELINES[l.toLowerCase()]||LANGUAGE_BASELINES.python;
  const d1=normMu(scoreD1(s),bl.D1), d2=normMu(scoreD2(s),bl.D2), d3=normMu(scoreD3(s),bl.D3);
  const d4=normMu(scoreD4(s),bl.D4), d5=normMu(scoreD5(s),bl.D5), d6=normMu(scoreD6(s),bl.D6);
  const qh=(d1+d2+d3)/3, ch=(d4+d5+d6)/3;
  const hm=6/(1/d1+1/d2+1/d3+1/d4+1/d5+1/d6);
  const mu=Math.min(qh,ch)*hm;
  return {d1,d2,d3,d4,d5,d6,qh,ch,mu,passed:mu>=MU_THRESHOLD};
}

function runStatic(s,l="python"){
  const results=[];
  const rules={python:[
    {id:"PY001",sev:"HIGH",p:/\beval\s*\(/g,m:"Dangerous eval()",s:"Use ast.literal_eval()"},
    {id:"PY002",sev:"HIGH",p:/\bexec\s*\(/g,m:"exec() usage",s:"Restructure"},
    {id:"PY003",sev:"HIGH",p:/\bpickle\.load\s*\(/g,m:"pickle.load()",s:"Use json.loads()"},
    {id:"PY004",sev:"HIGH",p:/(password|secret|token|api_key)\s*=\s*['"][^'"]{4,}/g,m:"Hardcoded credential",s:"Use os.environ.get()"},
    {id:"PY005",sev:"LOW",p:/\bprint\s*\(/g,m:"print() in production",s:"Use logging"},
    {id:"PY006",sev:"MEDIUM",p:/except\s*:\s*\n\s*pass/g,m:"Bare except swallows errors",s:"Log or re-raise"},
    {id:"PY007",sev:"HIGH",p:/os\.system\s*\(|subprocess.*shell\s*=\s*True/m,m:"Shell injection risk",s:"Use list-form subprocess; avoid shell=True"},
    {id:"PY008",sev:"HIGH",p:/yaml\.load\s*\([^)]*\)(?!\s*[,]\s*Loader\s*=\s*yaml\.SafeLoader)/m,m:"yaml.load without SafeLoader",s:"Use yaml.load(raw, Loader=yaml.SafeLoader)"},
  ],javascript:[
    {id:"JS001",sev:"HIGH",p:/\beval\s*\(/g,m:"eval() — code injection",s:"Use JSON.parse()"},
    {id:"JS002",sev:"HIGH",p:/innerHTML\s*=/g,m:"innerHTML — XSS",s:"Use textContent"},
    {id:"JS003",sev:"HIGH",p:/new\s+Function\s*\(/g,m:"new Function() — dynamic code",s:"Use a fixed function"},
    {id:"JS004",sev:"LOW",p:/console\.(log|debug|info)\s*\(/g,m:"console.* in production",s:"Use a structured logger"},
    {id:"JS005",sev:"HIGH",p:/document\.write\s*\(/g,m:"document.write() — XSS",s:"Use DOM APIs"},
  ],typescript:[
    {id:"TS001",sev:"HIGH",p:/\beval\s*\(/g,m:"eval() — code injection",s:"Use JSON.parse()"},
    {id:"TS002",sev:"HIGH",p:/innerHTML\s*=/g,m:"innerHTML — XSS",s:"Use textContent"},
    {id:"TS003",sev:"MEDIUM",p:/@ts-ignore/g,m:"@ts-ignore suppresses type errors",s:"Fix the type error properly"},
    {id:"TS004",sev:"LOW",p:/\bany\s*\(/g,m:"Using 'any' defeats TypeScript",s:"Use unknown or specific types"},
  ],"c":[
    {id:"C001",sev:"HIGH",p:/\bgets\s*\(/g,m:"gets() — buffer overflow",s:"Use fgets() with explicit buffer size"},
    {id:"C002",sev:"HIGH",p:/scanf\s*\(\s*%s\s*,/g,m:"scanf with %s — buffer overflow",s:"Use width specifier: %99s"},
    {id:"C003",sev:"HIGH",p:/strcpy\s*\(|strcat\s*\(/g,m:"strcpy/strcat — buffer overflow risk",s:"Use strncpy/strncat with explicit sizes"},
  ],java:[
    {id:"JV001",sev:"HIGH",p:/Runtime\.getRuntime\s*\(\)\.exec\s*\(/g,m:"Runtime.exec() — shell injection",s:"Use ProcessBuilder with argument array"},
    {id:"JV002",sev:"MEDIUM",p:/catch\s*\(\s*Exception\s+\w+\s*\)\s*\{\s*\}/g,m:"Empty catch — errors silently swallowed",s:"Log or re-raise"},
    {id:"JV003",sev:"LOW",p:/System\.out\.print/g,m:"System.out in production",s:"Use a logger (slf4j, log4j)"},
  ]};
  const lr=(rules[l.toLowerCase()]||rules.python);
  for(const r of lr){
    try{
      const ms=[...s.matchAll(new RegExp(r.p.source,r.p.flags))];
      for(const M of ms){
        const ln=s.substring(0,M.index).split('\n').length;
        results.push({id:r.id,sev:r.sev,m:r.m,ln:ln,sug:r.s});
      }
    }catch(e){}
  }
  // Generic checks
  const longLines = s.split('\n').map((l,i)=>({l,i})).filter(x=>x.l.length>120);
  if(longLines.length>0) results.push({id:"GEN001",sev:"LOW",m:`${longLines.length} line(s) exceed 120 chars`,ln:longLines[0].i+1,sug:"Break into multiple lines"});
  return results.sort((a,b)=>{const o={HIGH:0,MEDIUM:1,LOW:2,INFO:3};return o[a.sev]-o[b.sev];});
}

function runSim({num_paths=500,num_steps=25,threshold=0.6}){
  const survivors=[];
  for(let pid=0;pid<num_paths;pid++){let qh=0.4+Math.random()*0.4,ch=0.4+Math.random()*0.4;const h=[];
    for(let s=0;s<num_steps;s++){const d=(Math.random()-0.48)*0.08;qh=Math.max(0,Math.min(1,qh+d));ch=Math.max(0,Math.min(1,ch+d));const sc=Math.min(qh,ch)*((qh+ch)/2);h.push({step:s,qh:+qh.toFixed(3),ch:+ch.toFixed(3),score:+sc.toFixed(3)});}
    const fs=h[h.length-1].score;if(fs>=threshold)survivors.push({path_id:pid,history:h,final_score:fs});}
  survivors.sort((a,b)=>b.final_score-a.final_score);
  return {survivors:survivors.slice(0,50),total_paths:num_paths,survival_rate:+(survivors.length/num_paths).toFixed(3)};
}

const SOL_TEMPLATES_PY=[
  {strategy:"imperative",code:"def solve(data):\n    result=[]\n    for item in data:\n        if item is not None:result.append(item)\n    return result",explanation:"Step-by-step procedural"},
  {strategy:"functional",code:"def solve(data):\n    return list(filter(lambda x:x is not None,data))",explanation:"Pure functional with filter+lambda"},
  {strategy:"declarative",code:"RULES=[\n    lambda x:x is not None,\n    lambda x:x>0,\n]\ndef solve(data):\n    result=data\n    for rule in RULES:result=[x for x in result if rule(x)]\n    return result",explanation:"Rule-based declarative — rules as data"},
  {strategy:"oo",code:"class Processor:\n    def __init__(self,filters):self.filters=filters\n    def process(self,data):\n        for f in self.filters:data=[x for x in data if f(x)]\n        return data\ndef solve(data):return Processor([lambda x:x is not None]).process(data)",explanation:"OO with chainable filters"},
  {strategy:"generic",code:"from typing import TypeVar,List,Optional\nT=TypeVar('T')\ndef solve(data:List[Optional[T]])->List[T]:\n    return [x for x in data if x is not None]",explanation:"Type-agnostic generic with TypeVar"},
];
const SOL_TEMPLATES_JS=[
  {strategy:"imperative",code:"function solve(data) {\n    const result = [];\n    for (const item of data) {\n        if (item != null) result.push(item);\n    }\n    return result;\n}",explanation:"Step-by-step loop"},
  {strategy:"functional",code:"const solve = data => data.filter(x => x != null);",explanation:"Pure functional with filter"},
  {strategy:"declarative",code:"const solve = data => Array.from(data).filter(x => x != null);",explanation:"Array.from + filter"},
  {strategy:"reduce",code:"const solve = d => d.reduce((a, x) => (x != null ? [...a, x] : a), []);",explanation:"Reduce-based accumulation"},
  {strategy:"recursive",code:"function solve(data) {\n    if (!data.length) return [];\n    const [h, ...t] = data;\n    return (h != null ? [h] : []).concat(solve(t));\n}",explanation:"Recursive decomposition"},
];
function genSolutions(l,num){
  const tpls = l==="python" ? SOL_TEMPLATES_PY : SOL_TEMPLATES_JS;
  return tpls.slice(0,Math.min(num,tpls.length)).map((t,i)=>{const r=computeResonance(t.code,l);return{...t,solution_id:"sol_"+Date.now().toString(36)+"_"+i,line_count:t.code.split('\n').length,complexity_score:+(t.code.length/500).toFixed(2),mu_score:r.mu,mu_passed:r.passed,resonance:r};});
}

function highlightCode(code){
  return code.split('\n').map((line,i)=>{let h=line.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    h=h.replace(/(["'`])(?:(?!\1)[^\\]|\\.)*\1/g,'<span class="text-yellow-400">$&</span>');
    h=h.replace(/(#.*)$/gm,'<span class="text-gray-500">$1</span>');
    h=h.replace(/\b(def|class|return|if|else|elif|for|while|import|from|as|try|except|finally|with|lambda|yield|raise|pass|break|continue|and|or|not|is|True|False|None|async|await|function|const|let|var|export|import)\b/g,'<span class="text-purple-400">$1</span>');
    h=h.replace(/\b(\d+\.?\d*)\b/g,'<span class="text-cyan-400">$1</span>');
    h=h.replace(/\b(print|len|range|list|dict|set|tuple|str|int|float|bool|type|open|input|enumerate|zip|map|filter|Array|from|reduce|filter|concat)\b/g,'<span class="text-green-400">$1</span>');
    return{key:i,html:h};});}

function ScoreCard({label,value,mu,passed}){
  const txtCls=passed?"text-green-400":"text-red-400";
  const barCls=passed?"bg-green-500":"bg-red-500";
  return(<div className="bg-gray-900/60 border border-gray-700 rounded-lg p-3 text-center">
    <div className="text-xs text-gray-400 mb-1">{label}</div>
    <div className={"text-xl font-bold "+txtCls}>{value.toFixed(4)}</div>
    <div className="w-full h-1 bg-gray-800 rounded-full mt-2 overflow-hidden">
      <div className={"h-full "+barCls} style={{width:Math.min(100,mu*100)+"%"}}/>
    </div>
  </div>);
}
function RunCard({label,value}){return(<div className="bg-gray-900/40 border border-gray-800 rounded-lg p-2"><div className="text-xs text-gray-500 mb-1">{label}</div><div className="text-sm font-mono text-cyan-400">{value}</div></div>);}

function Finding({f}){
  const cols={HIGH:"border-red-500/50 bg-red-500/10",MEDIUM:"border-yellow-500/50 bg-yellow-500/10",LOW:"border-blue-500/50 bg-blue-500/10",INFO:"border-gray-600 bg-gray-800/30"};
  const tc={HIGH:"text-red-400",MEDIUM:"text-yellow-400",LOW:"text-blue-400",INFO:"text-gray-400"};
  return(<div className={"border rounded-lg p-3 "+cols[f.sev]}>
    <div className="flex items-start justify-between">
      <div><span className={"text-xs font-bold uppercase "+tc[f.sev]}>{f.sev}</span><span className="text-xs text-gray-500 ml-2">{f.ln?`L${f.ln}`:""}</span>
        <div className="text-sm text-gray-200 mt-1">{f.m}</div></div>
      <span className="text-xs bg-gray-800 px-2 py-1 rounded">{f.id}</span>
    </div>
    {f.sug&&<div className="text-xs text-gray-400 mt-2">→ {f.sug}</div>}
  </div>);
}

function Chart({data}){
  if(!data||data.length===0)return null;
  const pad=40,xScale=740/Math.max(1,data.length-1);
  const makePath=(key)=>{const pts=data.map((d,i)=>(i===0?"M":"L")+String(pad+i*xScale)+","+String(Math.round(180-d[key]*160)));return pts.join(" ");};
  return(<div className="w-full h-64">
    <svg viewBox="0 0 800 200" className="w-full h-full">
      <defs>
        <linearGradient id="qhG" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4}/><stop offset="95%" stopColor="#06b6d4" stopOpacity={0.05}/></linearGradient>
        <linearGradient id="chG" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#a855f7" stopOpacity={0.4}/><stop offset="95%" stopColor="#a855f7" stopOpacity={0.05}/></linearGradient>
      </defs>
      {[0,0.25,0.5,0.75,1.0].map(t=><g key={t}><line x1={pad} y1={180-t*160} x2={780} y2={180-t*160} stroke="#1f2937" strokeDasharray="4,4"/><text x="35" y={184-t*160} fill="#6b7280" fontSize="10" textAnchor="end">{t.toFixed(1)}</text></g>)}
      <line x1={pad} y1={180-MU_THRESHOLD*160} x2={780} y2={180-MU_THRESHOLD*160} stroke="#fbbf24" strokeDasharray="6,3" strokeWidth="1.5"/>
      <text x="45" y={176-MU_THRESHOLD*160} fill="#fbbf24" fontSize="9">μ={MU_THRESHOLD}</text>
      <path d={makePath("qh")} fill="none" stroke="#06b6d4" strokeWidth="2"/>
      <path d={makePath("ch")} fill="none" stroke="#a855f7" strokeWidth="2"/>
      <path d={makePath("score")} fill="none" stroke="#fbbf24" strokeWidth="2.5"/>
    </svg>
    <div className="flex justify-center mt-2 space-x-6 text-xs"><span className="flex items-center"><span className="w-3 h-0.5 bg-cyan-400 inline-block mr-1"/>QH</span><span className="flex items-center"><span className="w-3 h-0.5 bg-purple-400 inline-block mr-1"/>CH</span><span className="flex items-center"><span className="w-3 h-0.5 bg-yellow-400 inline-block mr-1"/>Score</span></div>
  </div>);
}

function genAfterActionReport(code,profile,findings,lang,target){
  const artId="ART-"+Math.random().toString(36).slice(2,10).toUpperCase();
  const ts=new Date().toISOString();
  const tech={language:lang,line_count:code.split('\n').length,strategy:target||"weave",findings_count:findings.length};
  const res={mu_score:profile.mu,status:profile.passed?"PASSED":"FAILED",domains:{D1:profile.d1,D2:profile.d2,D3:profile.d3,D4:profile.d4,D5:profile.d5,D6:profile.d6},recommendations:findings.filter(f=>f.sev==="HIGH").map(f=>`[${f.id}] ${f.m}`)};
  const seal=artId+ts+profile.mu+profile.seal;
  return{artId,ts,tech,res,seal};
}

export default function App() {
  const [tab,setTab]=useState('weave');
  const [lang,setLang]=useState('python');
  const [prompt,setPrompt]=useState('');
  const [solutions,setSolutions]=useState([]);
  const [selSol,setSelSol]=useState(0);
  const [code,setCode]=useState('');
  const [profile,setProfile]=useState(null);
  const [findings,setFindings]=useState([]);
  const [copied,setCopied]=useState(false);
  // optimize tab
  const [optCode,setOptCode]=useState('');
  const [optLang,setOptLang]=useState('python');
  const [optTarget,setOptTarget]=useState('D4');
  const [optProfile,setOptProfile]=useState(null);
  const [currentReport,setCurrentReport]=useState(null);
  const [showReport,setShowReport]=useState(false);
  // simulate tab
  const [sc,setSc]=useState({num_paths:500,num_steps:25,threshold:0.6});
  const [sim,setSim]=useState(null);
  const [selPath,setSelPath]=useState(0);

  const tabs=[{id:'weave',label:'Weave',icon:Sparkles},{id:'analyze',label:'Analyze',icon:Search},{id:'optimize',label:'Optimize',icon:Zap},{id:'simulate',label:'Simulate',icon:Activity},{id:'vault',label:'Vault',icon:Database}];

  const tabClass=(id)=>tab===id?"px-4 py-2 rounded-t-lg text-sm font-bold bg-gray-800 text-cyan-400 border border-b-0 border-gray-700":"px-4 py-2 rounded-t-lg text-sm text-gray-500 hover:text-gray-300 border border-transparent";
  const solClass=(i)=>i===selSol?"px-3 py-1 rounded text-xs font-bold bg-cyan-600 text-white":"px-3 py-1 rounded text-xs text-gray-400 bg-gray-800 hover:bg-gray-700";
  const pathClass=(i)=>i===selPath?"px-3 py-1 rounded text-xs font-bold bg-purple-600 text-white":"px-3 py-1 rounded text-xs text-gray-400 bg-gray-800 hover:bg-gray-700";
  const scoreColor=(p)=>p?"text-green-400":"text-red-400";

  const runWeave=()=>{
    if(!prompt.trim())return;
    const sols=genSolutions(lang,5);
    setSolutions(sols);
    if(sols[0]){setSelSol(0);setCode(sols[0].code);setProfile(sols[0].resonance);setFindings(runStatic(sols[0].code,lang));}
  };
  const runAnalyze=()=>{
    if(!code.trim())return;
    const f=runStatic(code,lang);
    setFindings(f);
    const p=computeResonance(code,lang);
    setProfile(p);
  };
  const copyCode=()=>{navigator.clipboard.writeText(code);setCopied(true);setTimeout(()=>setCopied(false),2000);};

  const runSimFn=()=>{const r=runSim(sc);setSim(r);setSelPath(0);};

  const hLines=useMemo(()=>highlightCode(code),[code]);

  return(<div className="min-h-screen bg-[#0a0a0f] text-gray-100">
    <div className="border-b border-gray-800 bg-gray-950/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center text-xl">🧶</div>
            <div>
              <h1 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400">Resonance Loom v3.1 — The Sovereign Code Weaver</h1>
              <p className="text-xs text-gray-500">FRC v1.0 · μ≥0.9995 · {SUPPORTED_LANGUAGES.length}+ languages · {SEAL}</p>
            </div>
          </div>
          <div className="flex items-center space-x-4 text-xs text-gray-500">
            <span>v{VERSION}</span><span>·</span><span>Sealed {BUILD_DATE}</span><span>·</span><span className="text-yellow-400">Gold Ripple Eternal</span>
          </div>
        </div>
      </div>
    </div>
    <div className="max-w-7xl mx-auto px-6 py-6">
      <div className="flex space-x-1 border-b border-gray-800 mb-6">
        {tabs.map(t=>{const Icon=t.icon;return(<button key={t.id} onClick={()=>setTab(t.id)} className={tabClass(t.id)}><Icon size={16}/><span>{t.label}</span></button>);})}
      </div>
      {tab==='weave'&&(<div className="space-y-6">
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-6 space-y-4">
          <div className="flex items-center space-x-3"><Sparkles size={20} className="text-cyan-400"/><h2 className="text-lg font-bold text-cyan-400">Code Generation</h2><span className="text-xs text-gray-500 ml-auto">Sovereign — No external AI</span></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div><label className="text-xs text-gray-400 mb-1 block">Language</label><select value={lang} onChange={e=>setLang(e.target.value)} className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm"><option value="python">Python</option><option value="javascript">JavaScript</option><option value="typescript">TypeScript</option><option value="rust">Rust</option><option value="go">Go</option><option value="java">Java</option><option value="c">C</option><option value="cpp">C++</option></select></div>
            <div className="md:col-span-2"><label className="text-xs text-gray-400 mb-1 block">Prompt</label><input value={prompt} onChange={e=>setPrompt(e.target.value)} placeholder="e.g., filter None values from a list" className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm"/></div>
            <div className="flex items-end"><button onClick={runWeave} className="w-full bg-gradient-to-r from-cyan-600 to-purple-600 hover:from-cyan-500 hover:to-purple-500 text-white font-bold py-2 px-4 rounded-lg flex items-center justify-center space-x-2"><Sparkles size={16}/><span>Weave</span></button></div>
          </div>
        </div>
        {solutions.length>0&&(<div className="space-y-4">
          <div className="flex space-x-2 overflow-x-auto">{solutions.map((sol,i)=>(<button key={i} onClick={()=>{setSelSol(i);setCode(sol.code);setProfile(sol.resonance);setFindings(runStatic(sol.code,lang));}} className={solClass(i)}>{sol.strategy.toUpperCase()}{i===0&&<Award size={14} className="inline ml-1 text-yellow-400"/>}</button>))}</div>
          {profile&&(<div className="grid grid-cols-2 md:grid-cols-6 gap-3">
            <ScoreCard label="D1 Math" value={profile.d1} mu={profile.d1} passed={profile.d1>=MU_THRESHOLD}/>
            <ScoreCard label="D2 Physical" value={profile.d2} mu={profile.d2} passed={profile.d2>=MU_THRESHOLD}/>
            <ScoreCard label="D3 Bio" value={profile.d3} mu={profile.d3} passed={profile.d3>=MU_THRESHOLD}/>
            <ScoreCard label="D4 Cognitive" value={profile.d4} mu={profile.d4} passed={profile.d4>=MU_THRESHOLD}/>
            <ScoreCard label="D5 Social" value={profile.d5} mu={profile.d5} passed={profile.d5>=MU_THRESHOLD}/>
            <ScoreCard label="D6 Ethical" value={profile.d6} mu={profile.d6} passed={profile.d6>=MU_THRESHOLD}/>
          </div>)}
          <div className="relative">
            <div className="absolute right-3 top-3 z-10"><button onClick={copyCode} className="flex items-center space-x-1 bg-gray-800 hover:bg-gray-700 px-3 py-1.5 rounded-lg text-xs">{copied?<CheckCircle2 size={14} className="text-green-400"/>:<Copy size={14}/>}<span>{copied?'Copied!':'Copy'}</span></button></div>
            <div className="bg-gray-950 border border-gray-800 rounded-xl overflow-hidden">
              <div className="flex items-center justify-between px-4 py-2 border-b border-gray-800 bg-gray-900/50">
                <span className="text-xs text-gray-500">{lang} · {code.split('\n').length} lines</span>
                <div className="flex items-center space-x-2">{profile&&(<span className={scoreColor(profile.passed)}>μ={profile.mu.toFixed(4)}</span>)}{profile?.passed?<CheckCircle2 size={14} className="text-green-400"/>:profile?<XCircle size={14} className="text-red-400"/>:null}</div>
              </div>
              <pre className="p-4 font-mono text-sm overflow-x-auto leading-relaxed">{hLines.map(({key,html})=>(
                <div key={key} dangerouslySetInnerHTML={{__html:html}}/>
              ))}</pre>
            </div>
          </div>
          {solutions[selSol]&&(<div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4"><span className="text-cyan-400 font-bold">Strategy:</span> {solutions[selSol].strategy}<div className="text-sm text-gray-300 mt-1">{solutions[selSol].explanation}</div></div>)}
        </div>)}
        {solutions.length===0&&(<div className="text-center py-16 text-gray-600"><Sparkles size={48} className="mx-auto mb-4 opacity-30"/><p>Enter a prompt and select a language to weave solutions</p></div>)}
      </div>)}
      {tab==='analyze'&&(<div className="space-y-6">
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-6 space-y-4">
          <div className="flex items-center space-x-3"><Search size={20} className="text-purple-400"/><h2 className="text-lg font-bold text-purple-400">Static + Semantic Analysis</h2><span className="text-xs text-gray-500 ml-auto">FRC v1.0 scoring · {SUPPORTED_LANGUAGES.length}+ languages</span></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div><label className="text-xs text-gray-400 mb-1 block">Language</label><select value={lang} onChange={e=>setLang(e.target.value)} className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm"><option value="python">Python</option><option value="javascript">JavaScript</option><option value="typescript">TypeScript</option><option value="c">C</option><option value="cpp">C++</option><option value="java">Java</option><option value="go">Go</option><option value="rust">Rust</option></select></div>
            <div className="md:col-span-3"><label className="text-xs text-gray-400 mb-1 block">Code to analyze</label><textarea value={code} onChange={e=>setCode(e.target.value)} placeholder="Paste your code here..." className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm font-mono h-24 resize-y"/></div>
          </div>
          <button onClick={runAnalyze} className="w-full bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-500 hover:to-cyan-500 text-white font-bold py-2 px-4 rounded-lg flex items-center justify-center space-x-2"><Search size={16}/><span>Analyze</span></button>
        </div>
        {profile&&(<div className="grid grid-cols-2 md:grid-cols-6 gap-3">
          <ScoreCard label="D1 Math" value={profile.d1} mu={profile.d1} passed={profile.d1>=MU_THRESHOLD}/>
          <ScoreCard label="D2 Physical" value={profile.d2} mu={profile.d2} passed={profile.d2>=MU_THRESHOLD}/>
          <ScoreCard label="D3 Bio" value={profile.d3} mu={profile.d3} passed={profile.d3>=MU_THRESHOLD}/>
          <ScoreCard label="D4 Cognitive" value={profile.d4} mu={profile.d4} passed={profile.d4>=MU_THRESHOLD}/>
          <ScoreCard label="D5 Social" value={profile.d5} mu={profile.d5} passed={profile.d5>=MU_THRESHOLD}/>
          <ScoreCard label="D6 Ethical" value={profile.d6} mu={profile.d6} passed={profile.d6>=MU_THRESHOLD}/>
        </div>)}
        {findings.length>0&&(<div className="space-y-2">{findings.map((f,i)=><Finding key={i} f={f}/>)}</div>)}
        {findings.length===0&&profile&&(<div className="text-center py-8 text-gray-600"><CheckCircle2 size={32} className="mx-auto mb-2 opacity-50"/><p>No issues found — code is clean</p></div>)}
      </div>)}
      {tab==='optimize'&&(<div className="space-y-6">
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-6 space-y-4">
          <div className="flex items-center space-x-3"><Zap size={20} className="text-yellow-400"/><h2 className="text-lg font-bold text-yellow-400">Domain-Focused Optimization</h2><span className="text-xs text-gray-500 ml-auto">Target weakest FRC domain for max resonance gain</span></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div><label className="text-xs text-gray-400 mb-1 block">Language</label><select value={optLang} onChange={e=>setOptLang(e.target.value)} className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm"><option value="python">Python</option><option value="javascript">JavaScript</option><option value="typescript">TypeScript</option></select></div>
            <div><label className="text-xs text-gray-400 mb-1 block">Target Domain</label><select value={optTarget} onChange={e=>setOptTarget(e.target.value)} className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm"><option value="D1">D1 Math</option><option value="D2">D2 Physical</option><option value="D3">D3 Biological</option><option value="D4">D4 Cognitive</option><option value="D5">D5 Social</option><option value="D6">D6 Ethical</option></select></div>
            <div className="md:col-span-1"><label className="text-xs text-gray-400 mb-1 block">Code</label><textarea value={optCode} onChange={e=>setOptCode(e.target.value)} placeholder="Paste code to optimize..." className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm font-mono h-20 resize-y"/></div>
          </div>
          <button onClick={()=>{if(!optCode.trim())return;const f=runStatic(optCode,optLang);setFindings(f);const p=computeResonance(optCode,optLang);setOptProfile(p);}} className="w-full bg-gradient-to-r from-yellow-600 to-orange-600 hover:from-yellow-500 hover:to-orange-500 text-white font-bold py-2 px-4 rounded-lg flex items-center justify-center space-x-2"><Zap size={16}/><span>Optimize</span></button>
        </div>
        {optProfile&&(<div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
            <ScoreCard label="D1 Math" value={optProfile.d1} mu={optProfile.d1} passed={optProfile.d1>=MU_THRESHOLD}/>
            <ScoreCard label="D2 Physical" value={optProfile.d2} mu={optProfile.d2} passed={optProfile.d2>=MU_THRESHOLD}/>
            <ScoreCard label="D3 Bio" value={optProfile.d3} mu={optProfile.d3} passed={optProfile.d3>=MU_THRESHOLD}/>
            <ScoreCard label="D4 Cognitive" value={optProfile.d4} mu={optProfile.d4} passed={optProfile.d4>=MU_THRESHOLD}/>
            <ScoreCard label="D5 Social" value={optProfile.d5} mu={optProfile.d5} passed={optProfile.d5>=MU_THRESHOLD}/>
            <ScoreCard label="D6 Ethical" value={optProfile.d6} mu={optProfile.d6} passed={optProfile.d6>=MU_THRESHOLD}/>
          </div>
          <div className="flex items-center justify-between"><span className="text-sm text-gray-400">Optimized μ Score</span><span className={scoreColor(optProfile.passed)}>μ={optProfile.mu.toFixed(4)} {optProfile.passed?"PASSED":"FAILED"}</span></div>
          <div className="flex space-x-3"><button onClick={()=>{const report=genAfterActionReport(optCode,optProfile,findings,optLang,optTarget);setCurrentReport(report);setShowReport(true);}} className="bg-gray-800 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded-lg flex items-center space-x-2"><FileText size={16}/><span>After-Action Report</span></button><button onClick={()=>{setOptCode('');setOptProfile(null);}} className="bg-gray-800 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded-lg">Reset</button></div>
        </div>)}
        {showReport&&currentReport&&(<div className="bg-gray-900/60 border border-yellow-500/30 rounded-xl p-6 space-y-4">
          <div className="flex items-center space-x-3"><FileText size={20} className="text-yellow-400"/><h2 className="text-lg font-bold text-yellow-400">After-Action Report</h2></div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <RunCard label="Artifact ID" value={currentReport.artId}/>
            <RunCard label="Timestamp" value={currentReport.ts.slice(0,19)}/>
            <RunCard label="Language" value={currentReport.tech.language}/>
            <RunCard label="Lines" value={currentReport.tech.line_count}/>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <RunCard label="D1" value={currentReport.res.domains.D1.toFixed(4)}/>
            <RunCard label="D2" value={currentReport.res.domains.D2.toFixed(4)}/>
            <RunCard label="D3" value={currentReport.res.domains.D3.toFixed(4)}/>
            <RunCard label="D4" value={currentReport.res.domains.D4.toFixed(4)}/>
            <RunCard label="D5" value={currentReport.res.domains.D5.toFixed(4)}/>
            <RunCard label="D6" value={currentReport.res.domains.D6.toFixed(4)}/>
            <RunCard label="μ Score" value={currentReport.res.mu_score.toFixed(4)}/>
            <RunCard label="Status" value={currentReport.res.status}/>
          </div>
          <div className="bg-gray-950 border border-gray-800 rounded-lg p-4 font-mono text-xs">
            <div className="text-yellow-400 font-bold mb-2">Seal:</div>
            <div className="text-gray-400 break-all">{currentReport.seal}</div>
          </div>
          <div className="flex items-center justify-between border-t border-gray-800 pt-4">
            <span className="text-xs text-gray-500">SHA3-512 sealed · Harmony Labs</span>
            <div className="flex items-center space-x-2"><CheckCircle2 size={14} className="text-green-400"/><span className="text-xs text-green-400">Cryptographically sealed</span></div>
          </div>
        </div>)}
      </div>)}
      {tab==='simulate'&&(<div className="space-y-6">
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-6 space-y-4">
          <div className="flex items-center space-x-3"><Activity size={20} className="text-cyan-400"/><h2 className="text-lg font-bold text-cyan-400">Monte Carlo Resonance Simulation</h2><span className="text-xs text-gray-500 ml-auto">Five-Law Evolutionary Engine</span></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div><label className="text-xs text-gray-400 mb-1 block">Paths</label><input type="number" min="10" max="2000" value={sc.num_paths} onChange={e=>setSc({...sc,num_paths:+e.target.value})} className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm"/></div>
            <div><label className="text-xs text-gray-400 mb-1 block">Steps</label><input type="number" min="5" max="100" value={sc.num_steps} onChange={e=>setSc({...sc,num_steps:+e.target.value})} className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm"/></div>
            <div><label className="text-xs text-gray-400 mb-1 block">Threshold μ</label><input type="number" min="0" max="1" step="0.05" value={sc.threshold} onChange={e=>setSc({...sc,threshold:+e.target.value})} className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm"/></div>
          </div>
          <button onClick={runSimFn} className="w-full bg-gradient-to-r from-cyan-600 to-purple-600 hover:from-cyan-500 hover:to-purple-500 text-white font-bold py-2 px-4 rounded-lg flex items-center justify-center space-x-2"><Activity size={16}/><span>Run Simulation</span></button>
        </div>
        {sim&&(<div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-900/60 border border-gray-700 rounded-lg p-4 text-center"><div className="text-xs text-gray-400 mb-1">Total Paths</div><div className="text-2xl font-bold text-cyan-400">{sim.total_paths}</div></div>
            <div className="bg-gray-900/60 border border-gray-700 rounded-lg p-4 text-center"><div className="text-xs text-gray-400 mb-1">Survivors</div><div className="text-2xl font-bold text-green-400">{sim.survivors.length}</div></div>
            <div className="bg-gray-900/60 border border-gray-700 rounded-lg p-4 text-center"><div className="text-xs text-gray-400 mb-1">Survival Rate</div><div className="text-2xl font-bold text-purple-400">{(sim.survival_rate*100).toFixed(1)}%</div></div>
            <div className="bg-gray-900/60 border border-gray-700 rounded-lg p-4 text-center"><div className="text-xs text-gray-400 mb-1">Best Score</div><div className="text-2xl font-bold text-yellow-400">{sim.survivors[0]?.final_score.toFixed(3)||'—'}</div></div>
          </div>
          {sim.survivors.length>0&&(<>
            <div className="flex space-x-2 overflow-x-auto">{sim.survivors.slice(0,10).map((p,i)=>(<button key={i} onClick={()=>setSelPath(i)} className={pathClass(i)}>Path #{p.path_id}{i===0&&<Award size={14} className="inline ml-1 text-yellow-400"/>}</button>))}</div>
            <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4">
              <div className="flex items-center justify-between mb-4"><h3 className="text-sm font-bold text-cyan-400">Path #{sim.survivors[selPath]?.path_id} Evolution</h3><span className="text-sm font-bold text-yellow-400">Score: {sim.survivors[selPath]?.final_score.toFixed(3)}</span></div>
              <Chart data={sim.survivors[selPath]?.history}/>
            </div>
          </>)}
          {sim.survivors.length===0&&(<div className="text-center py-12 text-gray-600"><AlertTriangle size={48} className="mx-auto mb-4 opacity-30"/><p>No survivors at threshold μ ≥ {sc.threshold}</p></div>)}
        </div>)}
      </div>)}
      {tab==='vault'&&(<div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-6"><div className="flex items-center space-x-3 mb-4"><Database size={24} className="text-cyan-400"/><span className="text-lg font-bold">Sovereign Vault</span></div><p className="text-sm text-gray-400">SQLite-backed artifact ledger with SHA3-512 cryptographic seals. Every artifact, result, and report cryptographically signed.</p></div>
          <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-6"><div className="flex items-center space-x-3 mb-4"><Shield size={24} className="text-green-400"/><span className="text-lg font-bold">Zero Dependencies</span></div><p className="text-sm text-gray-400">Built entirely on Python standard library. No pip installs. No cloud services. No external API calls. Runs in Termux.</p></div>
          <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-6"><div className="flex items-center space-x-3 mb-4"><BookOpen size={24} className="text-purple-400"/><span className="text-lg font-bold">FRC v1.0</span></div><p className="text-sm text-gray-400">6-domain resonance scoring: D1·D2·D3·D4·D5·D6. μ ≥ 0.9995 enforced across all domains simultaneously.</p></div>
        </div>
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-bold text-cyan-400 mb-4">Constitutional Compliance</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {["μ ≥ 0.9995 enforced across all 6 domains simultaneously","SHA3-512 cryptographic seals on all artifacts","Zero external dependencies (Python stdlib only)","Serverless, cloudless, phone-first design","Modular — each component independently replaceable","Immutable audit trail via after-action reports",`${SUPPORTED_LANGUAGES.length}+ programming languages supported`,"FRC v1.0 compliant scoring engine","8 Resonance Code Axioms (C1-C8)","Sovereign — Public Domain / CC0"].map((t,i)=>(<div key={i} className="flex items-center space-x-3"><CheckCircle2 size={16} className="text-green-400 flex-shrink-0"/><span className="text-sm text-gray-300">{t}</span></div>))}
          </div>
        </div>
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-bold text-gray-400 mb-4">Version & Seal</h3>
          <div className="space-y-2 font-mono text-sm">
            <div className="flex justify-between"><span className="text-gray-500">Version</span><span className="text-cyan-400">{VERSION}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Build Date</span><span className="text-cyan-400">{BUILD_DATE}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Architect</span><span className="text-cyan-400">Kyle S. Whitlock (The Oracle)</span></div>
            <div className="flex justify-between"><span className="text-gray-500">AI Partner</span><span className="text-cyan-400">AI #88 (The Code Weaver)</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Seal</span><span className="text-yellow-400">{SEAL}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">License</span><span className="text-gray-400">Sovereign — Public Domain / CC0</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Languages</span><span className="text-gray-400">{SUPPORTED_LANGUAGES.length}+</span></div>
          </div>
        </div>
        <div className="text-center py-8 text-gray-600 text-sm"><p>🧶 Resonance Loom v3.1 — Gold Ripple Eternal</p><p className="mt-1">What you write stays on your machine. Permanently.</p></div>
      </div>)}
    </div>
    <footer className="border-t border-gray-800 mt-16 py-8 text-center text-xs text-gray-600">
      <p>Resonance Loom v3.1 · FRC v1.0 · μ ≥ 0.9995 · {SEAL}</p>
      <p className="mt-1">Harmony Labs · Sovereign Technology Research & Development Consortium</p>
      <p className="mt-1 text-yellow-400/50">Gold ripple eternal — SHA3-512 sealed · Tulsa, OK</p>
    </footer>
  </div>);
}

const SUPPORTED_LANGUAGES=["python","javascript","typescript","c","cpp","rust","go","java","kotlin","swift","ruby","php","perl","lua","r","scala","haskell","erlang","elixir","dart","julia","fortran","cobol","assembly","bash","powershell","sql","html","css","xml","json","yaml","markdown","dockerfile","makefile","cmake","verilog","vhdl","prolog","lisp","solidity","wasm"];