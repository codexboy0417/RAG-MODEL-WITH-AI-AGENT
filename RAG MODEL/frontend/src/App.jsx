import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import HeroTablet from './components/HeroTablet';
import FeaturesSection from './components/FeaturesSection';
import InteractivePlayground from './components/InteractivePlayground';
import ApiKeyModal from './components/ApiKeyModal';

const DEFAULT_GROQ_KEY = import.meta.env.VITE_GROQ_API_KEY || "";
const DEFAULT_TAVILY_KEY = import.meta.env.VITE_TAVILY_API_KEY || "";

export default function App() {
  const [activeMode, setActiveMode] = useState('rag'); // 'rag' | 'agent'
  const [isPlaygroundOpen, setIsPlaygroundOpen] = useState(false);
  const [isKeyModalOpen, setIsKeyModalOpen] = useState(false);
  
  const [apiKey, setApiKey] = useState(DEFAULT_GROQ_KEY);
  const [tavilyKey, setTavilyKey] = useState(DEFAULT_TAVILY_KEY);

  useEffect(() => {
    const savedGroqKey = localStorage.getItem('pixelcore_groq_key');
    const savedTavilyKey = localStorage.getItem('pixelcore_tavily_key');
    if (savedGroqKey) setApiKey(savedGroqKey);
    if (savedTavilyKey) setTavilyKey(savedTavilyKey);
  }, []);

  const handleSaveKeys = (newGroqKey, newTavilyKey) => {
    setApiKey(newGroqKey);
    setTavilyKey(newTavilyKey);
    localStorage.setItem('pixelcore_groq_key', newGroqKey);
    localStorage.setItem('pixelcore_tavily_key', newTavilyKey);
  };

  const handleSelectMode = (mode) => {
    setActiveMode(mode);
  };

  return (
    <div className="min-h-screen bg-[#e9ecf0] text-slate-800 flex flex-col justify-between relative selection:bg-brand-orange selection:text-white">
      
      {/* ── Top Atmospheric Light Blobs ── */}
      <div className="fixed top-[-10%] left-[-10%] w-[500px] h-[500px] bg-white/40 rounded-full blur-3xl pointer-events-none -z-10" />
      <div className="fixed bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-orange-100/30 rounded-full blur-3xl pointer-events-none -z-10" />

      {/* ── Header with Branch Selector ── */}
      <Header
        apiKey={apiKey}
        activeMode={activeMode}
        onSelectMode={handleSelectMode}
        onOpenKeyModal={() => setIsKeyModalOpen(true)}
        onOpenPlayground={() => setIsPlaygroundOpen(true)}
      />

      {/* ── Main Content Area ── */}
      <main className="flex-1 flex flex-col items-center justify-center">
        {/* Hero Section with Branch Switcher & 3D Clay Scene */}
        <HeroTablet
          activeMode={activeMode}
          onSelectMode={handleSelectMode}
          onOpenPlayground={() => setIsPlaygroundOpen(true)}
          onOpenKeyModal={() => setIsKeyModalOpen(true)}
        />

        {/* Features & Architecture Section */}
        <FeaturesSection
          onOpenPlayground={() => setIsPlaygroundOpen(true)}
        />
      </main>

      {/* ── Footer ── */}
      <footer className="w-full max-w-7xl mx-auto px-4 sm:px-8 py-8 border-t border-slate-200/80 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-medium text-slate-500">
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded-lg bg-brand-orange flex items-center justify-center text-[10px] text-white font-bold">
            P
          </div>
          <span>PixelCore Dual AI Engine (RAG Model + AI Agent) © 2026.</span>
        </div>

        <div className="flex items-center gap-4">
          <button 
            onClick={() => {
              setActiveMode('rag');
              setIsPlaygroundOpen(true);
            }} 
            className="hover:text-brand-orange transition-colors font-bold"
          >
            1. RAG Model
          </button>
          <span>•</span>
          <button 
            onClick={() => {
              setActiveMode('agent');
              setIsPlaygroundOpen(true);
            }} 
            className="hover:text-brand-orange transition-colors font-bold"
          >
            2. AI Agent
          </button>
          <span>•</span>
          <button 
            onClick={() => setIsKeyModalOpen(true)} 
            className="hover:text-brand-orange transition-colors font-bold"
          >
            API Keys
          </button>
          <span>•</span>
          <span className="text-[10px] bg-slate-200/80 text-slate-700 px-2.5 py-1 rounded-full font-mono font-bold">
            Dual Engine Ready ▲
          </span>
        </div>
      </footer>

      {/* ── Modals & Drawers ── */}
      <InteractivePlayground
        isOpen={isPlaygroundOpen}
        onClose={() => setIsPlaygroundOpen(false)}
        apiKey={apiKey}
        tavilyKey={tavilyKey}
        activeMode={activeMode}
        onSelectMode={handleSelectMode}
        onOpenKeyModal={() => setIsKeyModalOpen(true)}
      />

      <ApiKeyModal
        isOpen={isKeyModalOpen}
        onClose={() => setIsKeyModalOpen(false)}
        apiKey={apiKey}
        tavilyKey={tavilyKey}
        onSaveKeys={handleSaveKeys}
      />

    </div>
  );
}
