import React, { useState, useEffect } from 'react';
import { ArrowUpRight, BarChart3, Cpu, Sparkles, Eye, ShieldCheck, Terminal } from 'lucide-react';

export default function FloatingClayElements({ onOpenDemo }) {
 const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
 const [eyeAngle, setEyeAngle] = useState(0);

 useEffect(() => {
 const handleMouseMove = (e) => {
 const { innerWidth, innerHeight } = window;
 const x = (e.clientX / innerWidth - 0.5) * 2; // -1 to 1
 const y = (e.clientY / innerHeight - 0.5) * 2;
 setMousePos({ x, y });

 // Calculate eyeball pupil tracking angle
 const angle = Math.atan2(e.clientY - innerHeight * 0.45, e.clientX - innerWidth * 0.65);
 setEyeAngle(angle);
 };

 window.addEventListener('mousemove', handleMouseMove);
 return () => window.removeEventListener('mousemove', handleMouseMove);
 }, []);

 return (
 <div className="relative w-full h-[460px] md:h-[520px] flex items-center justify-center select-none overflow-visible">
 {/* ── Background Giant PixelCore Watermark (Matching reference image) ── */}
 <div 
 className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-40 md:opacity-50 z-0 overflow-hidden"
 style={{
 transform: `translate(${mousePos.x * -10}px, ${mousePos.y * -8}px)`
 }}
 >
 <div className="text-[85px] sm:text-[130px] md:text-[160px] font-black pixel-watermark tracking-tighter leading-none select-none">
 Pixel<span className="text-brand-orange/30">Core</span>
 </div>
 </div>

 {/* ── 1. Top Right Performance Stat Badge (Matching reference: 240% PERFORMANCE) ── */}
 <div 
 className="absolute top-4 sm:top-8 right-2 sm:right-12 z-20 transition-transform duration-300 ease-out"
 style={{
 transform: `translate(${mousePos.x * 14}px, ${mousePos.y * 12}px)`
 }}
 >
 <div className="clay-card p-3 sm:p-4 flex items-center gap-3 sm:gap-4 bg-white/90 backdrop-blur-sm shadow-clay-card-sm border-2 border-white cursor-pointer hover:scale-105 transition-all">
 {/* Mini 3D bar chart icon */}
 <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-2xl bg-gradient-to-br from-white to-slate-100 shadow-[inset_2px_2px_4px_rgba(255,255,255,0.9),inset_-2px_-2px_4px_rgba(0,0,0,0.06),4px_4px_10px_rgba(0,0,0,0.08)] flex items-end justify-center p-2 gap-1 border border-white">
 <div className="w-1.5 h-3 bg-brand-orange rounded-full shadow-sm"></div>
 <div className="w-1.5 h-5 bg-brand-orange rounded-full shadow-sm"></div>
 <div className="w-1.5 h-7 bg-gradient-to-t from-brand-orange to-amber-400 rounded-full shadow-sm animate-pulse"></div>
 </div>
 <div>
 <div className="flex items-center gap-1">
 <span className="text-xl sm:text-2xl font-black text-slate-800 tracking-tight">240%</span>
 <ArrowUpRight className="w-4 h-4 text-brand-orange font-bold stroke-[3]" />
 </div>
 <div className="text-[10px] sm:text-xs font-bold uppercase tracking-wider text-slate-400">
 RAG Accuracy
 </div>
 </div>
 </div>
 </div>

 {/* ── 2. Top Center: 3D Clay Robotic Arm & Claw ── */}
 <div 
 className="absolute top-2 sm:top-6 left-[46%] -translate-x-1/2 z-20 transition-transform duration-200 pointer-events-none"
 style={{
 transform: `translate(calc(-50% + ${mousePos.x * 18}px), ${mousePos.y * 15}px) rotate(${mousePos.x * 4}deg)`
 }}
 >
 <div className="relative animate-floatSlow">
 {/* Base Arm Joint */}
 <div className="w-9 h-9 rounded-full bg-gradient-to-b from-amber-400 to-brand-orange shadow-[0_8px_16px_rgba(255,120,0,0.4),inset_2px_2px_4px_rgba(255,255,255,0.7),inset_-2px_-2px_4px_rgba(0,0,0,0.2)] flex items-center justify-center border-2 border-white/60 mx-auto">
 <div className="w-4 h-4 rounded-full bg-slate-800 shadow-inner"></div>
 </div>
 {/* Arm Beam */}
 <div className="w-5 h-12 bg-gradient-to-r from-orange-400 via-brand-orange to-orange-600 mx-auto rounded-full shadow-[inset_1px_1px_3px_rgba(255,255,255,0.8),inset_-1px_-1px_3px_rgba(0,0,0,0.2),2px_4px_8px_rgba(0,0,0,0.1)] -mt-1.5"></div>
 {/* Wrist Joint */}
 <div className="w-7 h-7 rounded-full bg-slate-700 shadow-[inset_1px_1px_2px_rgba(255,255,255,0.4),2px_4px_6px_rgba(0,0,0,0.2)] flex items-center justify-center mx-auto -mt-1 border border-slate-500">
 <div className="w-2.5 h-2.5 rounded-full bg-brand-orange animate-ping"></div>
 </div>
 {/* Dual Gripper Claws */}
 <div className="flex justify-between w-14 -mt-1 mx-auto">
 <div className="w-3.5 h-8 bg-brand-orange rounded-l-full shadow-md transform -rotate-12 border border-white/40"></div>
 <div className="w-3.5 h-8 bg-brand-orange rounded-r-full shadow-md transform rotate-12 border border-white/40"></div>
 </div>
 </div>
 </div>

 {/* ── 3. Top Left: Isometric Neural Data Cube ── */}
 <div 
 className="absolute top-6 sm:top-10 left-6 sm:left-14 z-10 transition-transform duration-300 pointer-events-none"
 style={{
 transform: `translate(${mousePos.x * -16}px, ${mousePos.y * -14}px) rotate(${mousePos.y * 5}deg)`
 }}
 >
 <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-2xl bg-white/70 backdrop-blur-md border-2 border-white shadow-[12px_12px_24px_#cfd5de,-8px_-8px_16px_#ffffff,inset_2px_2px_4px_rgba(255,255,255,0.9)] flex items-center justify-center p-2.5 animate-floatDelay">
 <div className="relative w-full h-full flex items-center justify-center">
 {/* Neural network nodes */}
 <div className="w-2 h-2 rounded-full bg-brand-orange absolute top-1 left-1 shadow-sm"></div>
 <div className="w-2 h-2 rounded-full bg-brand-orange absolute top-1 right-1 shadow-sm"></div>
 <div className="w-2 h-2 rounded-full bg-brand-orange absolute bottom-1 left-1 shadow-sm"></div>
 <div className="w-2 h-2 rounded-full bg-brand-orange absolute bottom-1 right-1 shadow-sm"></div>
 <div className="w-3 h-3 rounded-full bg-amber-500 absolute shadow-md"></div>
 {/* Connecting lines */}
 <div className="w-full h-0.5 bg-brand-orange/30 absolute"></div>
 <div className="h-full w-0.5 bg-brand-orange/30 absolute"></div>
 </div>
 </div>
 </div>

 {/* ── 4. Left: 3D Orange Clay Smartphone ── */}
 <div 
 className="absolute left-6 sm:left-14 md:left-20 top-28 sm:top-32 z-20 transition-transform duration-200 cursor-pointer"
 style={{
 transform: `translate(${mousePos.x * -14}px, ${mousePos.y * -10}px) rotate(${-12 + mousePos.x * 6}deg)`
 }}
 onClick={onOpenDemo}
 >
 <div className="w-24 sm:w-28 md:w-32 h-44 sm:h-52 md:h-56 rounded-[28px] bg-gradient-to-br from-[#ffa149] via-[#ff7800] to-[#e65c00] p-2 border-2 border-white/60 shadow-[18px_22px_35px_rgba(0,0,0,0.18),-10px_-10px_25px_rgba(255,255,255,0.9),inset_2px_2px_5px_rgba(255,255,255,0.7),inset_-3px_-3px_6px_rgba(0,0,0,0.25)] hover:scale-105 transition-all animate-float">
 {/* Camera bump */}
 <div className="w-10 h-10 rounded-2xl bg-white/20 backdrop-blur-sm border border-white/40 shadow-inner flex flex-col items-center justify-around p-1 mb-2">
 <div className="w-3.5 h-3.5 rounded-full bg-slate-900 border border-white/50 shadow-sm flex items-center justify-center">
 <div className="w-1 h-1 rounded-full bg-cyan-400"></div>
 </div>
 <div className="w-3.5 h-3.5 rounded-full bg-slate-900 border border-white/50 shadow-sm flex items-center justify-center">
 <div className="w-1 h-1 rounded-full bg-blue-400"></div>
 </div>
 </div>
 {/* Screen area with mini clay badge */}
 <div className="w-full h-24 sm:h-28 rounded-2xl bg-white/90 p-2 flex flex-col justify-between shadow-inner">
 <div className="flex items-center gap-1 text-[8px] font-bold text-slate-500">
 <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping"></span>
 Live Groq RAG
 </div>
 <div className="text-[9px] font-extrabold text-slate-800 line-clamp-2">
 Query: date +2
 </div>
 <div className="bg-brand-orange text-white text-[8px] font-bold rounded-lg px-1.5 py-0.5 text-center shadow-sm">
 Thursday Oct 1
 </div>
 </div>
 </div>
 </div>

 {/* ── 5. Centerpiece: 3D Clay Yellow/Orange Laptop ── */}
 <div 
 className="relative z-30 transition-transform duration-200 mt-6 sm:mt-10 cursor-pointer"
 style={{
 transform: `translate(${mousePos.x * 8}px, ${mousePos.y * 6}px) perspective(1000px) rotateX(${10 - mousePos.y * 8}deg) rotateY(${mousePos.x * 10}deg)`
 }}
 onClick={onOpenDemo}
 >
 <div className="relative group">
 {/* Laptop Screen Top Lid */}
 <div className="w-[260px] sm:w-[320px] md:w-[380px] h-[160px] sm:h-[190px] md:h-[230px] rounded-t-[28px] rounded-b-lg bg-gradient-to-b from-[#ffb429] via-[#ff9500] to-[#e67300] p-2.5 sm:p-3.5 border-4 border-white shadow-[0_-10px_25px_rgba(255,150,0,0.3),inset_3px_3px_6px_rgba(255,255,255,0.7),inset_-3px_-3px_6px_rgba(0,0,0,0.25)] mx-auto transform -rotate-x-12 origin-bottom transition-all">
 {/* Display Bezel & Screen */}
 <div className="w-full h-full rounded-2xl bg-slate-950 p-3 sm:p-4 flex flex-col justify-between border-2 border-slate-800 shadow-inner relative overflow-hidden">
 {/* Screen Header */}
 <div className="flex items-center justify-between border-b border-slate-800 pb-1.5">
 <div className="flex gap-1.5">
 <div className="w-2.5 h-2.5 rounded-full bg-rose-500 shadow-sm"></div>
 <div className="w-2.5 h-2.5 rounded-full bg-amber-500 shadow-sm"></div>
 <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-sm"></div>
 </div>
 <div className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
 <Terminal className="w-3 h-3 text-brand-orange" />
 rag_engine.py
 </div>
 </div>

 {/* Code / Interactive Output simulation */}
 <div className="font-mono text-[10px] sm:text-xs text-emerald-400 space-y-1 my-auto">
 <div className="text-slate-400">
 <span className="text-brand-orange">Q:</span> "date +2 days"
 </div>
 <div className="text-amber-300 flex items-center gap-1">
 <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping"></span>
 [Tool] calculate_relative_date()
 </div>
 <div className="text-white font-bold bg-slate-900/80 px-2 py-1 rounded-md border border-slate-800">
 Target: Thursday, 01 October
 </div>
 </div>

 {/* Screen footer status */}
 <div className="flex items-center justify-between text-[9px] text-slate-500 font-mono pt-1">
 <span>Model: qwen/qwen3.8-27b</span>
 <span className="text-emerald-400 font-bold">READY ●</span>
 </div>
 </div>
 </div>

 {/* Laptop Base (Keyboard + Trackpad) */}
 <div className="w-[300px] sm:w-[370px] md:w-[440px] h-[90px] sm:h-[110px] md:h-[130px] rounded-[24px] bg-gradient-to-b from-[#ffa726] via-[#ff8f00] to-[#e65100] p-3 border-4 border-white shadow-[0_25px_50px_rgba(0,0,0,0.22),inset_3px_3px_6px_rgba(255,255,255,0.7),inset_-4px_-4px_8px_rgba(0,0,0,0.3)] mx-auto -mt-2">
 {/* Keyboard Deck */}
 <div className="w-full h-12 sm:h-16 rounded-xl bg-slate-900/90 p-1.5 grid grid-cols-12 gap-0.5 border border-slate-800 shadow-inner">
 {Array.from({ length: 36 }).map((_, i) => (
 <div 
 key={i} 
 className="bg-slate-800/80 rounded-[3px] shadow-[inset_0.5px_0.5px_1px_rgba(255,255,255,0.2)] hover:bg-brand-orange transition-colors"
 />
 ))}
 </div>

 {/* Trackpad */}
 <div className="w-20 sm:w-24 h-6 sm:h-8 rounded-lg bg-gradient-to-b from-orange-400 to-amber-500 mx-auto mt-1.5 border border-white/40 shadow-[inset_1px_1px_2px_rgba(255,255,255,0.8),inset_-1px_-1px_2px_rgba(0,0,0,0.15)] flex items-center justify-center">
 <div className="w-6 h-0.5 bg-black/10 rounded-full"></div>
 </div>
 </div>
 </div>
 </div>

 {/* ── 6. Right: 3D Floating Sensor Eyeball ── */}
 <div 
 className="absolute right-8 sm:right-20 md:right-28 top-36 sm:top-40 z-20 transition-transform duration-200 pointer-events-none"
 style={{
 transform: `translate(${mousePos.x * 18}px, ${mousePos.y * 14}px)`
 }}
 >
 <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-gradient-to-b from-white via-[#f0f2f5] to-[#d6dbe4] border-4 border-white shadow-[14px_18px_30px_rgba(0,0,0,0.15),-8px_-8px_20px_#ffffff,inset_3px_3px_6px_rgba(255,255,255,0.9),inset_-3px_-3px_6px_rgba(0,0,0,0.15)] flex items-center justify-center p-2 animate-float">
 {/* Eyeball Iris */}
 <div 
 className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-gradient-to-br from-amber-400 via-brand-orange to-red-600 shadow-md flex items-center justify-center transition-transform duration-75"
 style={{
 transform: `translate(${Math.cos(eyeAngle) * 5}px, ${Math.sin(eyeAngle) * 5}px)`
 }}
 >
 {/* Pupil */}
 <div className="w-4 h-4 sm:w-5 sm:h-5 rounded-full bg-slate-950 flex items-center justify-center relative">
 <div className="w-1.5 h-1.5 rounded-full bg-white absolute top-0.5 right-0.5 shadow-sm"></div>
 </div>
 </div>
 </div>
 </div>

 {/* ── 7. Bottom Left: 3D Ceramic Microchip with Gold Leads ── */}
 <div 
 className="absolute bottom-6 sm:bottom-12 left-10 sm:left-24 z-20 transition-transform duration-300 pointer-events-none"
 style={{
 transform: `translate(${mousePos.x * -10}px, ${mousePos.y * -8}px) rotate(${15 + mousePos.x * 5}deg)`
 }}
 >
 <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-2xl bg-white border-2 border-white shadow-[12px_14px_25px_#cfd5de,-8px_-8px_16px_#ffffff,inset_2px_2px_4px_rgba(255,255,255,0.9),inset_-2px_-2px_4px_rgba(0,0,0,0.06)] flex items-center justify-center p-2.5 animate-floatDelay">
 <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-amber-400 to-brand-orange shadow-[inset_1px_1px_3px_rgba(255,255,255,0.8),inset_-1px_-1px_3px_rgba(0,0,0,0.2),2px_2px_5px_rgba(0,0,0,0.15)] flex items-center justify-center border border-white/60">
 <Cpu className="w-4 h-4 text-white stroke-[2.5]" />
 </div>
 </div>
 </div>

 {/* ── 8. Bottom Center: Floating Orange Clay Torus (Donut) ── */}
 <div 
 className="absolute bottom-4 sm:bottom-8 left-[40%] z-10 transition-transform duration-300 pointer-events-none"
 style={{
 transform: `translate(${mousePos.x * 12}px, ${mousePos.y * 10}px) rotateX(${60 + mousePos.y * 10}deg) rotateZ(${mousePos.x * 15}deg)`
 }}
 >
 <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-full border-[10px] sm:border-[12px] border-brand-orange bg-transparent shadow-[0_12px_25px_rgba(255,120,0,0.45),inset_2px_2px_4px_rgba(255,255,255,0.7),inset_-2px_-2px_4px_rgba(0,0,0,0.25)] animate-float"></div>
 </div>

 {/* ── 9. Bottom Right: Sensor Cable & Orb ── */}
 <div 
 className="absolute bottom-8 sm:bottom-12 right-12 sm:right-32 z-10 transition-transform duration-200 pointer-events-none"
 style={{
 transform: `translate(${mousePos.x * 16}px, ${mousePos.y * 12}px)`
 }}
 >
 <div className="relative">
 {/* Black curved wire indicator */}
 <div className="w-20 h-10 border-b-4 border-r-4 border-slate-800 rounded-br-3xl -top-6 -left-12 absolute opacity-80"></div>
 {/* Orange Spherical sensor */}
 <div className="w-8 h-8 rounded-full bg-gradient-to-br from-amber-400 to-brand-orange shadow-[4px_6px_12px_rgba(255,106,0,0.4),inset_1.5px_1.5px_3px_rgba(255,255,255,0.8)] border border-white/60 flex items-center justify-center">
 <div className="w-2 h-2 rounded-full bg-slate-900"></div>
 </div>
 </div>
 </div>
 </div>
 );
}
