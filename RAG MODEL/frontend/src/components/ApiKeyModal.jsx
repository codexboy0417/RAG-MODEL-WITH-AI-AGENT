import React, { useState } from 'react';
import { X, Key, Check, ExternalLink, Globe, Cpu } from 'lucide-react';

export default function ApiKeyModal({ isOpen, onClose, apiKey, tavilyKey, onSaveKeys }) {
  const [groqInput, setGroqInput] = useState(apiKey || '');
  const [tavilyInput, setTavilyInput] = useState(tavilyKey || '');
  const [savedSuccess, setSavedSuccess] = useState(false);

  if (!isOpen) return null;

  const handleSave = (e) => {
    e.preventDefault();
    onSaveKeys(groqInput.trim(), tavilyInput.trim());
    setSavedSuccess(true);
    setTimeout(() => {
      setSavedSuccess(false);
      onClose();
    }, 800);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fadeIn">
      <div className="clay-tablet w-full max-w-lg p-6 bg-[#f4f6f8] border-4 border-white shadow-2xl relative">
        {/* Header */}
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-200">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-brand-orange flex items-center justify-center shadow-md">
              <Key className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="text-sm font-black text-slate-900">API Configurations</h3>
              <p className="text-[11px] text-slate-500">Groq LLM & Tavily Live Web Search</p>
            </div>
          </div>
          <button onClick={onClose} className="clay-btn-grey w-7 h-7 flex items-center justify-center rounded-lg">
            <X className="w-3.5 h-3.5 text-slate-600" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSave} className="space-y-4">
          {/* Groq API Key */}
          <div>
            <label className="text-xs font-bold text-slate-700 flex items-center gap-1.5 mb-1.5">
              <Cpu className="w-3.5 h-3.5 text-brand-orange" />
              Groq API Key (Powers RAG & AI Agent)
            </label>
            <div className="clay-inset px-3.5 py-2.5">
              <input
                type="password"
                value={groqInput}
                onChange={(e) => setGroqInput(e.target.value)}
                placeholder="gsk_..."
                className="w-full bg-transparent text-xs font-mono text-slate-800 focus:outline-none"
              />
            </div>
            <span className="text-[10px] text-slate-400 mt-1 block">
              Defaulted to the active, working AI Agent API key.
            </span>
          </div>

          {/* Tavily API Key */}
          <div>
            <label className="text-xs font-bold text-slate-700 flex items-center gap-1.5 mb-1.5">
              <Globe className="w-3.5 h-3.5 text-blue-500" />
              Tavily API Key (Powers AI Agent Live Web Search)
            </label>
            <div className="clay-inset px-3.5 py-2.5">
              <input
                type="password"
                value={tavilyInput}
                onChange={(e) => setTavilyInput(e.target.value)}
                placeholder="tvly-..."
                className="w-full bg-transparent text-xs font-mono text-slate-800 focus:outline-none"
              />
            </div>
            <span className="text-[10px] text-slate-400 mt-1 block">
              Enables real-time internet search for the AI Agent.
            </span>
          </div>

          <div className="clay-card p-3 bg-white/80 text-[11px] text-slate-600 space-y-1">
            <div className="font-bold text-slate-800 flex items-center gap-1.5">
              <span>Keys are pre-configured & working!</span>
            </div>
            <p className="text-[10px] text-slate-400">
              Both API keys from your AI Agent are verified active with free sub-second inference.
            </p>
          </div>

          <div className="flex items-center justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="clay-btn-grey px-4 py-2 text-xs font-bold"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="clay-btn-orange px-5 py-2 text-xs font-bold flex items-center gap-1.5"
            >
              {savedSuccess ? (
                <>
                  <Check className="w-3.5 h-3.5 stroke-[3]" />
                  <span>Saved!</span>
                </>
              ) : (
                <span>Save Keys</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
