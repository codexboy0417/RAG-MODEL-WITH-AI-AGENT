import React from 'react';
import { FileSearch, Clock, ShieldCheck, Zap, ArrowRight, Layers, Cpu, Sparkles, Bot, Globe, Calculator, BookOpen } from 'lucide-react';

export default function FeaturesSection({ onOpenPlayground }) {
 const features = [
 {
 icon: BookOpen,
 tag: "BRANCH 01",
 title: "RAG Document Q&A",
 desc: "Extract text from structured PDFs and image screenshots via Tesseract OCR. Overlapping chunk embeddings ensure pinpoint, 100% grounded answers.",
 badge: " Document Vectorization"
 },
 {
 icon: Bot,
 tag: "BRANCH 02",
 title: "Autonomous AI Agent",
 desc: "LangChain tool-calling engine equipped with live Tavily Web Search and Wikipedia lookups. Autonomously chooses the best tool for each sub-task.",
 badge: " Multi-Tool ReAct"
 },
 {
 icon: Calculator,
 tag: "BRANCH 03",
 title: "Real-Time Tools & Math",
 desc: "Direct execution of relative time math (e.g. 'date +2') and arithmetic tools (add & multiply) with zero hallucination.",
 badge: " Zero Hallucination"
 },
 {
 icon: Zap,
 tag: "BRANCH 04",
 title: "Groq LPU Acceleration",
 desc: "Powered by Groq's Language Processing Units with verified openai/gpt-oss-20b model for instant sub-second responses.",
 badge: " Sub-Second Speed"
 }
 ];

 return (
 <section id="features-section" className="w-full max-w-7xl mx-auto px-4 sm:px-8 py-12 md:py-20">
 
 {/* Section Header */}
 <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
 <div>
 <div className="text-xs font-mono font-bold text-brand-orange uppercase tracking-widest mb-2 flex items-center gap-1.5">
 <Sparkles className="w-3.5 h-3.5" />
 DUAL ENGINE ARCHITECTURE
 </div>
 <h2 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">
 Engineered for Precision & Intelligence
 </h2>
 </div>
 <p className="text-xs sm:text-sm text-slate-500 font-medium max-w-md">
 A dual-branch system combining document RAG vector search and an autonomous multi-tool AI Agent into one unified, elegant web interface.
 </p>
 </div>

 {/* Feature Cards Grid with Claymorphism */}
 <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
 {features.map((f, i) => {
 const Icon = f.icon;
 return (
 <div 
 key={i} 
 className="clay-card p-6 flex flex-col justify-between hover:-translate-y-2 transition-all duration-300 group bg-[#f8f9fa] border-2 border-white cursor-pointer"
 onClick={onOpenPlayground}
 >
 <div>
 {/* Icon well */}
 <div className="w-12 h-12 rounded-2xl bg-white p-3 border-2 border-white shadow-[inset_1.5px_1.5px_3px_rgba(255,255,255,0.9),inset_-1.5px_-1.5px_3px_rgba(0,0,0,0.05),6px_6px_12px_rgba(0,0,0,0.06)] flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
 <Icon className="w-6 h-6 text-brand-orange stroke-[2.2]" />
 </div>

 <div className="text-[10px] font-mono font-bold text-slate-400 tracking-wider mb-1">
 {f.tag}
 </div>
 <h3 className="text-lg font-black text-slate-800 tracking-tight mb-2 group-hover:text-brand-orange transition-colors">
 {f.title}
 </h3>
 <p className="text-xs text-slate-500 leading-relaxed mb-6 font-medium">
 {f.desc}
 </p>
 </div>

 <div className="pt-4 border-t border-slate-200/60 flex items-center justify-between">
 <span className="text-[10px] font-bold text-slate-600">
 {f.badge}
 </span>
 <ArrowRight className="w-4 h-4 text-brand-orange group-hover:translate-x-1.5 transition-transform" />
 </div>
 </div>
 );
 })}
 </div>

 {/* Interactive Bottom Banner */}
 <div className="mt-12 clay-tablet p-6 sm:p-8 flex flex-col md:flex-row items-center justify-between gap-6 bg-gradient-to-r from-slate-900 to-slate-800 text-white border-2 border-slate-700/60">
 <div className="space-y-1 text-center md:text-left">
 <span className="text-xs font-mono font-bold text-brand-orange tracking-widest uppercase">
 Two Features In One UI
 </span>
 <h3 className="text-xl sm:text-2xl font-black tracking-tight">
 Switch seamlessly between RAG Model & AI Agent
 </h3>
 <p className="text-xs text-slate-400 max-w-lg">
 Use the branch selector at the top or in the hero section to toggle between Document Q&A and Autonomous Tool Calling at any time.
 </p>
 </div>
 <button
 onClick={onOpenPlayground}
 className="clay-btn-orange px-6 py-3.5 text-xs font-black flex items-center gap-2 cursor-pointer flex-shrink-0"
 >
 <span>OPEN LIVE STUDIO</span>
 <ArrowRight className="w-4 h-4 stroke-[3]" />
 </button>
 </div>

 </section>
 );
}
