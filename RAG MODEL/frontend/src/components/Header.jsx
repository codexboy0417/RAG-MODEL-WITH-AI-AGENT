import React from 'react';
import { Menu, ChevronLeft, Key, Sparkles, BookOpen, Bot } from 'lucide-react';

export default function Header({ onOpenKeyModal, onOpenPlayground, apiKey, activeMode, onSelectMode }) {
  return (
    <header className="w-full flex flex-col sm:flex-row items-center justify-between py-4 px-4 sm:px-8 max-w-7xl mx-auto z-40 relative gap-3 sm:gap-0">
      {/* ── Brand Logo ── */}
      <div 
        className="flex items-center gap-3 cursor-pointer group" 
        onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
      >
        {/* Pixelcore Orange Icon */}
        <div className="w-10 h-10 rounded-2xl bg-white p-2 border-2 border-white shadow-[6px_6px_14px_#cfd5de,-4px_-4px_10px_#ffffff,inset_1px_1px_2px_rgba(255,255,255,0.9)] flex items-center justify-center group-hover:scale-105 transition-transform">
          <div className="grid grid-cols-2 gap-1 w-full h-full">
            <div className="bg-brand-orange rounded-[3px] shadow-sm"></div>
            <div className="bg-amber-400 rounded-[3px] shadow-sm"></div>
            <div className="bg-amber-400 rounded-[3px] shadow-sm"></div>
            <div className="bg-brand-orange rounded-[3px] shadow-sm"></div>
          </div>
        </div>
        <div className="flex flex-col">
          <span className="font-extrabold text-xl tracking-tight text-slate-800 flex items-center gap-1.5">
            Pixel<span className="text-brand-orange">core</span>
            <span className="text-[10px] font-bold uppercase bg-brand-orange/10 text-brand-orange px-2 py-0.5 rounded-full border border-brand-orange/20">
              DUAL AI ENGINE
            </span>
          </span>
        </div>
      </div>

      {/* ── Center: Branch / Feature Selector Pill ── */}
      <div className="flex items-center p-1 bg-white/90 border-2 border-white rounded-2xl shadow-[4px_4px_10px_#cfd5de,-3px_-3px_8px_#ffffff]">
        <button
          onClick={() => {
            onSelectMode('rag');
            onOpenPlayground();
          }}
          className={`flex items-center gap-1.5 px-3 sm:px-4 py-1.5 rounded-xl text-xs font-black transition-all cursor-pointer ${
            activeMode === 'rag'
              ? 'clay-btn-orange text-white shadow-md'
              : 'text-slate-600 hover:text-brand-orange hover:bg-slate-100/60'
          }`}
          title="Switch to RAG Model Feature (Document Q&A)"
        >
          <BookOpen className="w-3.5 h-3.5" />
          <span>1. RAG Model</span>
        </button>

        <button
          onClick={() => {
            onSelectMode('agent');
            onOpenPlayground();
          }}
          className={`flex items-center gap-1.5 px-3 sm:px-4 py-1.5 rounded-xl text-xs font-black transition-all cursor-pointer ${
            activeMode === 'agent'
              ? 'clay-btn-orange text-white shadow-md'
              : 'text-slate-600 hover:text-brand-orange hover:bg-slate-100/60'
          }`}
          title="Switch to AI Agent Feature (Tools, Tavily & Wikipedia)"
        >
          <Bot className="w-3.5 h-3.5" />
          <span>2. AI Agent</span>
        </button>
      </div>

      {/* ── Right Actions (Menu + Key status) ── */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* API Key Status Pill */}
        <button
          onClick={onOpenKeyModal}
          className="clay-pill px-3.5 py-2 flex items-center gap-2 text-xs font-bold text-slate-700 hover:text-brand-orange transition-all cursor-pointer"
          title="Configure API Keys"
        >
          <Key className="w-3.5 h-3.5 text-brand-orange" />
          <span className="hidden sm:inline">
            {apiKey ? 'API Keys Active' : 'Set Keys'}
          </span>
          <span className={`w-2 h-2 rounded-full ${apiKey ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-amber-400'}`}></span>
        </button>

        {/* Dark Clay Menu Button */}
        <button 
          onClick={onOpenPlayground}
          className="clay-btn-dark w-10 h-10 flex items-center justify-center cursor-pointer"
          title="Open AI Studio"
        >
          <Menu className="w-4 h-4 text-white" />
        </button>

        {/* Collapse / Arrow button */}
        <button 
          onClick={onOpenPlayground}
          className="clay-btn-grey w-10 h-10 flex items-center justify-center cursor-pointer"
          title="Expand Interactive Studio"
        >
          <ChevronLeft className="w-4 h-4 text-slate-700" />
        </button>
      </div>
    </header>
  );
}
