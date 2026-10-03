import React from 'react';
import { ChevronsRight, BookOpen, Bot, Sparkles, Globe, Calculator, FileSearch } from 'lucide-react';
import FloatingClayElements from './FloatingClayElements';

export default function HeroTablet({ onOpenPlayground, onOpenKeyModal, activeMode, onSelectMode }) {
  return (
    <section className="w-full max-w-7xl mx-auto px-2 sm:px-4 md:px-8 py-2 md:py-6">
      {/* ── Outer Massive Clay Tablet Frame ── */}
      <div className="clay-tablet p-4 sm:p-8 md:p-12 relative overflow-hidden transition-all duration-300">
        
        {/* Subtle decorative grid/dots in background */}
        <div 
          className="absolute inset-0 opacity-[0.03] pointer-events-none"
          style={{
            backgroundImage: 'radial-gradient(#000000 1.5px, transparent 1.5px)',
            backgroundSize: '24px 24px'
          }}
        />

        {/* ── Top Row Content ── */}
        <div className="relative z-20 flex flex-col md:flex-row md:items-start justify-between gap-6 pointer-events-none">
          {/* Top Left: Main Headline & Step Indicator */}
          <div className="max-w-md pointer-events-auto">
            <div className="text-xs sm:text-sm font-mono font-bold text-slate-400 mb-2 tracking-widest flex items-center gap-2">
              <span>〔 DUAL ARCHITECTURE 〕</span>
              <span className="text-[10px] bg-brand-orange/10 text-brand-orange px-2 py-0.5 rounded-full font-bold">
                {activeMode === 'rag' ? 'FEATURE 1 ACTIVE' : 'FEATURE 2 ACTIVE'}
              </span>
            </div>
            <h1 className="text-3xl sm:text-4xl md:text-5xl font-black text-slate-900 leading-[1.08] tracking-tight">
              {activeMode === 'rag' ? (
                <>
                  RAG ENGINE<br />
                  <span className="text-slate-800">DOCUMENT Q&A</span><br />
                  <span className="text-brand-orange">ZERO HALLUCINATION</span>
                </>
              ) : (
                <>
                  AI AGENT<br />
                  <span className="text-slate-800">AUTONOMOUS TOOLS</span><br />
                  <span className="text-brand-orange">LIVE WEB & MATH</span>
                </>
              )}
            </h1>
          </div>

          {/* Top Right: Branch Selector Card in Hero */}
          <div className="md:text-right max-w-sm pointer-events-auto self-end md:self-start w-full md:w-auto">
            <div className="clay-card p-3 sm:p-4 bg-white/95 text-left border-2 border-white shadow-md">
              <span className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-widest block mb-2">
                Select Feature Branch
              </span>
              <div className="grid grid-cols-2 gap-2">
                {/* Branch 1 */}
                <button
                  onClick={() => onSelectMode('rag')}
                  className={`p-2.5 rounded-xl border text-left transition-all cursor-pointer flex flex-col justify-between gap-1.5 ${
                    activeMode === 'rag'
                      ? 'bg-orange-50 border-brand-orange text-slate-900 shadow-sm'
                      : 'border-slate-200 hover:border-slate-300 text-slate-600 bg-white'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <BookOpen className={`w-4 h-4 ${activeMode === 'rag' ? 'text-brand-orange' : 'text-slate-400'}`} />
                    <span className={`text-[9px] font-black px-1.5 py-0.2 rounded ${activeMode === 'rag' ? 'bg-brand-orange text-white' : 'bg-slate-100 text-slate-500'}`}>
                      1ST
                    </span>
                  </div>
                  <div>
                    <div className="text-xs font-black">RAG Model</div>
                    <div className="text-[10px] text-slate-400 font-medium leading-tight">PDFs & Vector Search</div>
                  </div>
                </button>

                {/* Branch 2 */}
                <button
                  onClick={() => onSelectMode('agent')}
                  className={`p-2.5 rounded-xl border text-left transition-all cursor-pointer flex flex-col justify-between gap-1.5 ${
                    activeMode === 'agent'
                      ? 'bg-orange-50 border-brand-orange text-slate-900 shadow-sm'
                      : 'border-slate-200 hover:border-slate-300 text-slate-600 bg-white'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <Bot className={`w-4 h-4 ${activeMode === 'agent' ? 'text-brand-orange' : 'text-slate-400'}`} />
                    <span className={`text-[9px] font-black px-1.5 py-0.2 rounded ${activeMode === 'agent' ? 'bg-brand-orange text-white' : 'bg-slate-100 text-slate-500'}`}>
                      2ND
                    </span>
                  </div>
                  <div>
                    <div className="text-xs font-black">AI Agent</div>
                    <div className="text-[10px] text-slate-400 font-medium leading-tight">Tavily, Wiki & Math</div>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* ── Centerpiece 3D Clay Scene ── */}
        <div className="my-2 sm:my-4 relative z-10">
          <FloatingClayElements onOpenDemo={onOpenPlayground} />
        </div>

        {/* ── Bottom Row Content ── */}
        <div className="relative z-20 flex flex-col md:flex-row md:items-end justify-between gap-6 pt-2 pointer-events-none">
          {/* Bottom Left: Value Proposition & CTA Buttons */}
          <div className="max-w-md pointer-events-auto space-y-4">
            <p className="text-xs sm:text-sm text-slate-600 font-medium leading-relaxed">
              {activeMode === 'rag' ? (
                <>
                  <strong>Feature 1: RAG Model</strong> — Ingest complex PDFs, execute OCR on images, 
                  and perform vector similarity search with 100% source-labeled answers.
                </>
              ) : (
                <>
                  <strong>Feature 2: AI Agent</strong> — Autonomous multi-tool assistant with live Tavily Web Search, 
                  Wikipedia encyclopedic lookups, and exact arithmetic tools with multi-step reasoning.
                </>
              )}
            </p>

            {/* CTA Buttons */}
            <div className="flex items-center gap-3 pt-1">
              <button
                onClick={onOpenPlayground}
                className="clay-btn-orange px-6 sm:px-7 py-3.5 flex items-center gap-2.5 text-xs sm:text-sm cursor-pointer group"
              >
                <span>{activeMode === 'rag' ? 'LAUNCH RAG MODEL' : 'LAUNCH AI AGENT'}</span>
                <ChevronsRight className="w-4 h-4 stroke-[3] group-hover:translate-x-1 transition-transform" />
              </button>

              <button
                onClick={() => {
                  onSelectMode(activeMode === 'rag' ? 'agent' : 'rag');
                  onOpenPlayground();
                }}
                className="clay-btn-grey px-5 sm:px-6 py-3.5 text-xs sm:text-sm cursor-pointer"
              >
                {activeMode === 'rag' ? 'SWITCH TO AI AGENT' : 'SWITCH TO RAG MODEL'}
              </button>
            </div>
          </div>

          {/* Bottom Center Pill: Scroll to explore more */}
          <div className="flex justify-center w-full md:w-auto pointer-events-auto mx-auto md:mx-0">
            <div 
              onClick={() => {
                const el = document.getElementById('features-section');
                if (el) el.scrollIntoView({ behavior: 'smooth' });
              }}
              className="clay-card px-5 py-2.5 flex flex-col items-center gap-1 cursor-pointer hover:bg-white transition-all text-center group"
            >
              <div className="w-4 h-6 rounded-full border-2 border-slate-400 flex items-start justify-center p-1">
                <div className="w-1 h-1.5 bg-brand-orange rounded-full animate-bounce"></div>
              </div>
              <span className="text-[11px] font-bold text-slate-500 group-hover:text-brand-orange transition-colors">
                Explore Architecture
              </span>
            </div>
          </div>
        </div>

      </div>
    </section>
  );
}
