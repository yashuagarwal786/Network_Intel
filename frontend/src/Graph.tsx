import {useEffect,useRef,useState} from 'react';
import cytoscape from 'cytoscape';
import {Plus,Minus,RotateCcw} from 'lucide-react';
import type {Entity,Relationship as Edge} from './demoTypes';
import {labColors} from './designTokens';
export const colors:Record<string,string>={Person:labColors.blue,Phone:labColors.cyan,Account:labColors.green,Vehicle:labColors.amber,Location:labColors.rose,Organization:labColors.purple};
type Props={entities:Entity[];edges:Edge[];path:string[];focus:string;selected:string;onSelect:(id:string,edge:boolean)=>void;fit:number;overview:boolean};
export default function Graph({entities,edges,path,focus,selected,onSelect,fit,overview}:Props){
 const container=useRef<HTMLDivElement>(null),cy=useRef<cytoscape.Core|null>(null),select=useRef(onSelect),signature=useRef(''),needsFit=useRef(true),lastPath=useRef('');select.current=onSelect;
 const [zoom,setZoom]=useState(100);
 useEffect(()=>{
  if(!container.current)return;
  const instance=cytoscape({container:container.current,elements:[],layout:{name:'preset'},autoungrabify:false,minZoom:.72,maxZoom:2.5,wheelSensitivity:.18,style:[
   {selector:'node',style:{label:'data(display_label)','background-color':labColors.elevated,'border-color':'data(color)','border-width':2,color:labColors.text,'font-size':17,'font-weight':500,'text-valign':'bottom','text-margin-y':10,width:40,height:40,'text-background-color':labColors.workspace,'text-background-opacity':.96,'text-background-padding':'4px','transition-property':'border-width, opacity, background-color','transition-duration':140}},
   {selector:'node[id="amit"]',style:{'text-valign':'top','text-margin-y':-9}},
   {selector:'node[type="Account"]',style:{shape:'hexagon'}},
   {selector:'node[type="Phone"]',style:{shape:'round-rectangle',width:25,height:39}},
   {selector:'node[type="Location"]',style:{shape:'round-triangle'}},
   {selector:'node[type="Vehicle"]',style:{shape:'diamond',width:40,height:40}},
   {selector:'node[type="Organization"]',style:{shape:'round-rectangle'}},
   {selector:'edge',style:{label:'',width:1.8,'line-color':'#655F59','target-arrow-color':'#847B73','target-arrow-shape':'triangle','curve-style':'bezier',color:labColors.secondary,'font-size':12,'text-rotation':'autorotate','text-background-color':labColors.workspace,'text-background-opacity':1,'text-background-padding':'3px','transition-property':'line-color, width, opacity','transition-duration':140}},
   {selector:'edge[verification_status="EXTRACTED_UNVERIFIED"], edge[verification_status="UNVERIFIED"]',style:{'line-style':'dashed','line-color':'#6b7280','target-arrow-color':'#6b7280'}},
   {selector:'edge[verification_status="INVESTIGATOR_VERIFIED"], edge[verification_status="VERIFIED"]',style:{'line-color':labColors.green,'target-arrow-color':labColors.green,width:2.4}},
   {selector:'edge[verification_status="INVESTIGATOR_CORROBORATED"]',style:{'line-color':'#06b6d4','target-arrow-color':'#06b6d4',width:3.2}},
   {selector:'edge[verification_status="INFERRED_CANDIDATE"], edge[status="inferred"]',style:{'line-style':'dotted','line-color':labColors.purple,width:2}},
   {selector:'edge.highlight,edge.hovered,edge.picked',style:{label:'data(label)'}},
   {selector:'.faded',style:{opacity:.08}},
   {selector:'node:active',style:{'border-width':4,'background-color':'#493027'}},
   {selector:'node.highlight',style:{'border-color':labColors.cyan,'border-width':4,'background-color':'#3A2922'}},
   {selector:'edge.highlight',style:{'line-color':labColors.cyan,'target-arrow-color':labColors.cyan,width:4}},
   {selector:'node.picked',style:{'border-color':labColors.cyan,'border-width':4,'background-color':'#523329',color:labColors.text}},
   {selector:'edge.picked',style:{'line-color':labColors.cyan,'target-arrow-color':labColors.cyan,width:4}},
  ]});
  cy.current=instance;instance.on('mouseover','edge',e=>e.target.addClass('hovered'));instance.on('mouseout','edge',e=>e.target.removeClass('hovered'));
  instance.on('tap','node',e=>select.current(e.target.id(),false));instance.on('tap','edge',e=>select.current(e.target.id(),true));
  instance.on('zoom',()=>setZoom(Math.round(instance.zoom()*100)));
  // Resize without refitting: opening a drawer must not move the user's graph.
  const observer=new ResizeObserver(()=>{instance.resize();if(needsFit.current&&container.current?.clientWidth&&container.current?.clientHeight){instance.fit(undefined,38);needsFit.current=false}});observer.observe(container.current);
  return()=>{observer.disconnect();instance.destroy();cy.current=null;signature.current=''};
 },[]);
 useEffect(()=>{
  const instance=cy.current;if(!instance)return;
  const next=JSON.stringify([entities,edges,overview]);if(signature.current===next)return;signature.current=next;
  const anchors:Record<string,{x:number;y:number}>={rahul:{x:0,y:0},P101:{x:170,y:0},P204:{x:340,y:0},amit:{x:510,y:0},A17:{x:510,y:110},A31:{x:340,y:110},vikram:{x:170,y:110}};
  const extra=entities.filter(n=>!anchors[n.id]).map(n=>n.id);
  instance.batch(()=>{instance.elements().remove();instance.add([...entities.map((n,i)=>({data:{...n,color:colors[n.type]},position:overview?{x:(i%6)*190,y:Math.floor(i/6)*120}:anchors[n.id]||([{x:0,y:110},{x:680,y:110},{x:680,y:0}][extra.indexOf(n.id)]||{x:(extra.indexOf(n.id)%5)*170,y:225+Math.floor(extra.indexOf(n.id)/5)*105})})),...edges.map(e=>({data:{...e,label:e.type.replaceAll('_',' ')+(e.evidence_ids.length?' ▪':'')}}))])});needsFit.current=true;instance.resize();if(container.current?.clientWidth&&container.current?.clientHeight){instance.fit(undefined,38);needsFit.current=false}
 },[entities,edges,overview]);
 useEffect(()=>{const instance=cy.current;if(!instance)return;instance.batch(()=>{instance.elements().removeClass('highlight faded picked');if(path.length)instance.elements().addClass('faded');path.forEach(id=>instance.getElementById(id).removeClass('faded').addClass('highlight'));if(selected)instance.getElementById(selected).removeClass('faded').addClass('picked')});if(focus)instance.center(instance.getElementById(focus));const pathKey=path.join('|');if(pathKey!==lastPath.current&&path.length&&container.current?.clientWidth){instance.fit(undefined,38)}lastPath.current=pathKey},[path,focus,selected,entities,edges,overview]);
 useEffect(()=>{cy.current?.fit(undefined,38)},[fit]);
 function changeZoom(factor:number){const c=cy.current;if(c)c.zoom({level:Math.max(c.minZoom(),Math.min(c.maxZoom(),c.zoom()*factor)),renderedPosition:{x:c.width()/2,y:c.height()/2}})}
 return <><div ref={container} className="graph" data-testid="entity-graph" data-selected={selected} data-path-count={path.length} aria-label="Interactive entity graph. Equivalent keyboard controls are available in search, path selectors and the evidence drawer."/><div className="graph-controls"><button aria-label="Zoom in" title="Zoom in" disabled={zoom>=250} onClick={()=>changeZoom(1.2)}><Plus size={15}/></button><output aria-label="Graph zoom">{zoom}%</output><button aria-label="Zoom out" title="Zoom out" disabled={zoom<=72} onClick={()=>changeZoom(1/1.2)}><Minus size={15}/></button><button aria-label="Reset graph view" title="Restore layout and fit" onClick={()=>cy.current?.fit(undefined,38)}><RotateCcw size={15}/></button></div></>;
}
