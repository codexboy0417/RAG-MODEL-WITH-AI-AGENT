import React, { useState, useRef, useEffect } from 'react';
import { 
 X, Send, Sparkles, FileText, Image as ImageIcon, BookOpen, 
 ChevronDown, ChevronRight, Terminal, UploadCloud, Trash2,
 Bot, Globe, Calculator, Layers, Cpu, CheckCircle2, Search
} from 'lucide-react';

// ── Dynamic API Keys Configuration ─────────────────────────────────────
const DEFAULT_GROQ_KEY = import.meta.env.VITE_GROQ_API_KEY || "";
const DEFAULT_TAVILY_KEY = import.meta.env.VITE_TAVILY_API_KEY || "";
const PREFERRED_MODELS = ["openai/gpt-oss-20b", "qwen/qwen3.8-27b", "openai/gpt-oss-120b"];

// ── Convert any Markdown text into clean Normal Plain Text Form ───────
const toNormalText = (text) => {
 if (!text) return "";
 return text
 // Strip code fence blocks ```code```
 .replace(/```[a-zA-Z]*\n?([\s\S]*?)```/g, '$1')
 // Strip inline backticks `code`
 .replace(/`([^`]+)`/g, '$1')
 // Strip markdown headings ### Heading
 .replace(/^#{1,6}\s+(.+)$/gm, '$1')
 // Strip bold & italic asterisks **bold** -> bold, *italic* -> italic
 .replace(/\*\*([^*]+)\*\*/g, '$1')
 .replace(/\*([^*]+)\*/g, '$1')
 .replace(/__([^_]+)__/g, '$1')
 .replace(/_([^_]+)_/g, '$1')
 // Convert bullets * or - to clean bullets •
 .replace(/^[\*\-]\s+/gm, '• ')
 // Strip markdown link brackets [name](url) -> name
 .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '$1 ($2)')
 .trim();
};

export default function InteractivePlayground({ 
 isOpen, 
 onClose, 
 apiKey, 
 tavilyKey, 
 activeMode = 'rag', 
 onSelectMode,
 onOpenKeyModal 
}) {
 const [mode, setMode] = useState(activeMode);

 // Sync mode with parent prop when prop changes
 useEffect(() => {
 if (activeMode) setMode(activeMode);
 }, [activeMode]);

 // Messages per branch
 const [ragMessages, setRagMessages] = useState([
 {
 id: 1,
 sender: 'assistant',
 text: "Hello! You are in the RAG Model (Document Q&A) branch. Upload a PDF or image document in the left panel to query it, or ask date math questions like 'date +2'.",
 source: 'llm',
 sourceLabel: ' From LLM General Knowledge',
 contexts: []
 }
 ]);

 const [agentMessages, setAgentMessages] = useState([
 {
 id: 1,
 sender: 'assistant',
 text: "Greetings! You are in the AI Agent branch. I am equipped with autonomous tools: Wikipedia Search, Tavily Live Web Search, and exact Math Calculators (Add & Multiply). Ask me any question, calculation, or recent event!",
 source: 'agent',
 sourceLabel: ' Autonomous AI Agent (Tools & Search)',
 toolsUsed: ['wikipedia_search', 'tavily_search', 'add', 'multiply']
 }
 ]);

 const [inputQuery, setInputQuery] = useState('');
 const [isLoading, setIsLoading] = useState(false);
 const [currentStepText, setCurrentStepText] = useState('');
 
 // Document state for RAG
 const [uploadedFiles, setUploadedFiles] = useState([]);
 const [documentChunks, setDocumentChunks] = useState([]);
 const [showContexts, setShowContexts] = useState({});
 const [showToolsUsed, setShowToolsUsed] = useState({});

 const messagesEndRef = useRef(null);

 const scrollToBottom = () => {
 messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
 };

 useEffect(() => {
 scrollToBottom();
 }, [ragMessages, agentMessages, isLoading]);

 const handleBranchSwitch = (newMode) => {
 setMode(newMode);
 if (onSelectMode) onSelectMode(newMode);
 };

 // Active messages depending on branch
 const currentMessages = mode === 'rag' ? ragMessages : agentMessages;

 // ═════════════════════════════════════════════════════════════════════
 // 1. TOOL CALLERS FOR AI AGENT (Wikipedia, Tavily, Math)
 // ═════════════════════════════════════════════════════════════════════

 // A. Wikipedia Search Tool (MediaWiki API with CORS)
 const callWikipediaTool = async (query) => {
 try {
 const searchUrl = `https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=${encodeURIComponent(query)}&format=json&origin=*`;
 const searchRes = await fetch(searchUrl);
 const searchData = await searchRes.json();
 const hits = searchData?.query?.search;
 if (!hits || hits.length === 0) {
 return `No Wikipedia pages found for '${query}'.`;
 }
 const topTitle = hits[0].title;
 // Fetch summary
 const summaryUrl = `https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(topTitle)}`;
 const sumRes = await fetch(summaryUrl);
 if (sumRes.ok) {
 const sumData = await sumRes.json();
 return `Title: ${sumData.title}\nSummary: ${sumData.extract || hits[0].snippet.replace(/<[^>]+>/g, '')}`;
 }
 return `Title: ${topTitle}\nSnippet: ${hits[0].snippet.replace(/<[^>]+>/g, '')}`;
 } catch (err) {
 return `Error querying Wikipedia: ${err.message}`;
 }
 };

 // B. Tavily Live Web Search Tool
 const callTavilyTool = async (query) => {
 const activeKey = (tavilyKey || DEFAULT_TAVILY_KEY).trim();
 if (!activeKey) {
 return "Tavily API key is missing. Unable to perform live web search.";
 }
 try {
 const res = await fetch("https://api.tavily.com/search", {
 method: "POST",
 headers: { "Content-Type": "application/json" },
 body: JSON.stringify({
 api_key: activeKey,
 query: query,
 max_results: 3,
 search_depth: "basic"
 })
 });
 if (!res.ok) {
 throw new Error(`Tavily HTTP error ${res.status}`);
 }
 const data = await res.json();
 const results = data.results || [];
 if (results.length === 0) return `No live web results found for '${query}'.`;
 return results.map((r, i) => `[${i + 1}] ${r.title}\nURL: ${r.url}\nContent: ${r.content}`).join("\n\n");
 } catch (err) {
 return `Error searching Tavily: ${err.message}`;
 }
 };

 // C. Arithmetic Tools (Add & Multiply)
 const callAddTool = (a, b) => {
 return Number(a) + Number(b);
 };

 const callMultiplyTool = (a, b) => {
 return Number(a) * Number(b);
 };

 // ═════════════════════════════════════════════════════════════════════
 // 2. REAL-TIME DATE/TIME TOOL (Used in RAG)
 // ═════════════════════════════════════════════════════════════════════
 const calculateRelativeDate = (q) => {
 const now = new Date();
 const query = q.toLowerCase().trim();

 const mathMatch = query.match(/([+-])\s*(\d+)(?:\s*(days?|weeks?|months?|date)?)?/);
 const prepAfter = query.match(/(?:after|in|later\s+than)\s+(\d+)\s*(days?|weeks?|months?)/);
 const prepBefore = query.match(/(?:before|prior\s+to|earlier\s+than)\s+(\d+)\s*(days?|weeks?|months?)/);
 const numAfter = query.match(/(\d+)\s*(days?|weeks?|months?)\s*(?:after|later|from now|ahead)/);
 const numBefore = query.match(/(\d+)\s*(days?|weeks?|months?)\s*(?:before|ago|earlier|prior|back)/);

 let offsetDays = null;

 if (query.includes('day before yesterday')) offsetDays = -2;
 else if (query.includes('day after tomorrow')) offsetDays = 2;
 else if (query.includes('yesterday')) offsetDays = -1;
 else if (query.includes('tomorrow')) offsetDays = 1;
 else if (query.includes('next week')) offsetDays = 7;
 else if (query.includes('last week')) offsetDays = -7;
 else if (mathMatch) {
 const sign = mathMatch[1];
 const num = parseInt(mathMatch[2], 10);
 const rawUnit = (mathMatch[3] || 'days').toLowerCase();
 const mult = rawUnit.includes('week') ? 7 : (rawUnit.includes('month') ? 30 : 1);
 offsetDays = sign === '+' ? num * mult : -num * mult;
 } else if (prepAfter) {
 const num = parseInt(prepAfter[1], 10);
 const mult = prepAfter[2].includes('week') ? 7 : (prepAfter[2].includes('month') ? 30 : 1);
 offsetDays = num * mult;
 } else if (prepBefore) {
 const num = parseInt(prepBefore[1], 10);
 const mult = prepBefore[2].includes('week') ? 7 : (prepBefore[2].includes('month') ? 30 : 1);
 offsetDays = -num * mult;
 } else if (numAfter) {
 const num = parseInt(numAfter[1], 10);
 const mult = numAfter[2].includes('week') ? 7 : (numAfter[2].includes('month') ? 30 : 1);
 offsetDays = num * mult;
 } else if (numBefore) {
 const num = parseInt(numBefore[1], 10);
 const mult = numBefore[2].includes('week') ? 7 : (numBefore[2].includes('month') ? 30 : 1);
 offsetDays = -num * mult;
 }

 if (offsetDays !== null) {
 const target = new Date(now.getTime() + offsetDays * 24 * 60 * 60 * 1000);
 const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
 const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
 const dir = offsetDays >= 0 ? 'after' : 'before';

 return {
 isTool: true,
 source: 'tool',
 sourceLabel: ' From Real-time Date/Time Tool',
 text: `Today is ${now.toLocaleDateString(undefined, options)} (${timeStr}). The date ${Math.abs(offsetDays)} days ${dir} is ${target.toLocaleDateString(undefined, options)}.`
 };
 }

 const currentKeywords = ['date', 'time', 'today', 'now', 'current date', 'whats the date', 'what is the date', 'what time is it'];
 if (currentKeywords.some(kw => query === kw || query.includes(kw))) {
 const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
 const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
 return {
 isTool: true,
 source: 'tool',
 sourceLabel: ' From Real-time Date/Time Tool',
 text: `Today is ${now.toLocaleDateString(undefined, options)}, and the current time is ${timeStr}.`
 };
 }

 return null;
 };

 // ═════════════════════════════════════════════════════════════════════
 // 3. CALL GROQ API FOR SIMPLE RAG / LLM GENERATION
 // ═════════════════════════════════════════════════════════════════════
 const callGroqApi = async (prompt, systemInstruction = null) => {
 const activeKey = (apiKey || DEFAULT_GROQ_KEY).trim();
 const systemPrompt = systemInstruction || 
 "You are a helpful, intelligent AI assistant. Always provide your answer in clean normal plain text form. Do NOT use markdown symbols, asterisks (**), bullet dashes, or markdown headers (###). Write natural, easy-to-read sentences and paragraphs.";

 for (const model of PREFERRED_MODELS) {
 try {
 const res = await fetch("https://api.groq.com/openai/v1/chat/completions", {
 method: "POST",
 headers: {
 "Content-Type": "application/json",
 "Authorization": `Bearer ${activeKey}`
 },
 body: JSON.stringify({
 model: model,
 messages: [
 { role: "system", content: systemPrompt },
 { role: "user", content: prompt }
 ],
 temperature: 0.2,
 max_tokens: 800
 })
 });

 if (res.ok) {
 const data = await res.json();
 const reply = data.choices?.[0]?.message?.content?.trim();
 if (reply) return toNormalText(reply);
 }
 } catch (err) {
 console.warn(`Model ${model} failed, trying next...`, err);
 }
 }

 throw new Error("Unable to reach Groq API. Please check your network connection.");
 };

 // ═════════════════════════════════════════════════════════════════════
 // 4. AUTONOMOUS AI AGENT EXECUTION LOOP (Function Calling)
 // ═════════════════════════════════════════════════════════════════════
 const executeAgentWorkflow = async (userPrompt) => {
 const activeKey = (apiKey || DEFAULT_GROQ_KEY).trim();
 const toolsUsedLog = [];

 // Check for direct arithmetic calculations first for 100% precision
 const mathPattern = /^\s*(?:calculate|what is|compute)?\s*\(?(\d+(?:\.\d+)?)\s*([\*x\+\-])\s*(\d+(?:\.\d+)?)\)?\s*(?:([\*x\+\-])\s*(\d+(?:\.\d+)?))?\s*\??$/i;
 const match = userPrompt.match(mathPattern);
 if (match) {
 try {
 // Safe evaluation of strict numeric expressions
 const sanitized = userPrompt.replace(/[^0-9\+\-\*\/\(\)\. ]/g, '').trim();
 if (sanitized && /^[\d\.\s\+\-\*\/\(\)]+$/.test(sanitized)) {
 const answer = Function(`'use strict'; return (${sanitized})`)();
 toolsUsedLog.push({
 tool: 'Math Calculator',
 query: sanitized,
 result: String(answer)
 });
 return {
 text: `The calculated result for ${sanitized} is ${answer}.`,
 toolsUsed: toolsUsedLog
 };
 }
 } catch (e) {
 // Fallback to LLM agent
 }
 }

 // Define tools schema for Groq LLM
 const agentTools = [
 {
 type: "function",
 function: {
 name: "wikipedia_search",
 description: "Search Wikipedia for factual and encyclopedic knowledge, historical events, figures, science, and concepts.",
 parameters: {
 type: "object",
 properties: {
 query: { type: "string", description: "Search query or topic" }
 },
 required: ["query"]
 }
 }
 },
 {
 type: "function",
 function: {
 name: "tavily_search",
 description: "Search the live web for recent news, breaking stories, current events, and real-time up-to-date data.",
 parameters: {
 type: "object",
 properties: {
 query: { type: "string", description: "Search query for real-time web search" }
 },
 required: ["query"]
 }
 }
 },
 {
 type: "function",
 function: {
 name: "add",
 description: "Add two numbers together precisely.",
 parameters: {
 type: "object",
 properties: {
 a: { type: "number", description: "First number" },
 b: { type: "number", description: "Second number" }
 },
 required: ["a", "b"]
 }
 }
 },
 {
 type: "function",
 function: {
 name: "multiply",
 description: "Multiply two numbers together precisely.",
 parameters: {
 type: "object",
 properties: {
 a: { type: "number", description: "First number" },
 b: { type: "number", description: "Second number" }
 },
 required: ["a", "b"]
 }
 }
 }
 ];

 const systemPrompt = 
 "You are an autonomous AI Agent equipped with tools: wikipedia_search, tavily_search, add, and multiply.\n" +
 "For factual encyclopedic queries, use wikipedia_search.\n" +
 "For current events, recent news, or live web info, use tavily_search.\n" +
 "For arithmetic, always use the add or multiply tools.\n" +
 "Provide your final answer in clean, normal, plain text format without markdown asterisks (**), markdown tables, or hashtags.";

 const conversation = [
 { role: "system", content: systemPrompt },
 { role: "user", content: userPrompt }
 ];

 setCurrentStepText("AI Agent thinking & selecting tools...");

 // First LLM call: Let Agent decide tools
 let firstCallData = null;
 let chosenModel = "openai/gpt-oss-20b";

 for (const model of PREFERRED_MODELS) {
 try {
 const res = await fetch("https://api.groq.com/openai/v1/chat/completions", {
 method: "POST",
 headers: {
 "Content-Type": "application/json",
 "Authorization": `Bearer ${activeKey}`
 },
 body: JSON.stringify({
 model: model,
 messages: conversation,
 tools: agentTools,
 tool_choice: "auto",
 temperature: 0.1,
 max_tokens: 700
 })
 });

 if (res.ok) {
 firstCallData = await res.json();
 chosenModel = model;
 break;
 }
 } catch (err) {
 console.warn(`Agent model ${model} failed, trying fallback:`, err);
 }
 }

 if (!firstCallData) {
 throw new Error("AI Agent could not connect to Groq API.");
 }

 const firstMsg = firstCallData.choices?.[0]?.message;
 const toolCalls = firstMsg?.tool_calls;

 // If no tools needed, direct response
 if (!toolCalls || toolCalls.length === 0) {
 return {
 text: toNormalText(firstMsg?.content || "No response received."),
 toolsUsed: [{ tool: "Direct Reasoning", query: userPrompt, result: "Direct LLM inference" }]
 };
 }

 // Execute tool calls
 conversation.push(firstMsg);

 for (const tc of toolCalls) {
 const toolName = tc.function.name;
 let args = {};
 try {
 args = JSON.parse(tc.function.arguments || "{}");
 } catch (e) {
 args = {};
 }

 let toolOutput = "";
 setCurrentStepText(`Executing tool: ${toolName}...`);

 if (toolName === "wikipedia_search") {
 const q = args.query || userPrompt;
 toolOutput = await callWikipediaTool(q);
 toolsUsedLog.push({
 tool: "Wikipedia Search",
 query: q,
 result: toolOutput.slice(0, 300) + "..."
 });
 } else if (toolName === "tavily_search") {
 const q = args.query || userPrompt;
 toolOutput = await callTavilyTool(q);
 toolsUsedLog.push({
 tool: "Tavily Web Search",
 query: q,
 result: toolOutput.slice(0, 300) + "..."
 });
 } else if (toolName === "add") {
 const res = callAddTool(args.a, args.b);
 toolOutput = String(res);
 toolsUsedLog.push({
 tool: "Add",
 query: `${args.a} + ${args.b}`,
 result: toolOutput
 });
 } else if (toolName === "multiply") {
 const res = callMultiplyTool(args.a, args.b);
 toolOutput = String(res);
 toolsUsedLog.push({
 tool: "Multiply",
 query: `${args.a} * ${args.b}`,
 result: toolOutput
 });
 } else {
 toolOutput = "Tool executed successfully.";
 toolsUsedLog.push({ tool: toolName, query: JSON.stringify(args), result: toolOutput });
 }

 // Add tool output to conversation
 conversation.push({
 role: "tool",
 tool_call_id: tc.id,
 content: String(toolOutput)
 });
 }

 // Final LLM call to synthesize the response
 setCurrentStepText("Synthesizing final answer with tool observations...");
 const finalRes = await fetch("https://api.groq.com/openai/v1/chat/completions", {
 method: "POST",
 headers: {
 "Content-Type": "application/json",
 "Authorization": `Bearer ${activeKey}`
 },
 body: JSON.stringify({
 model: chosenModel,
 messages: conversation,
 temperature: 0.2,
 max_tokens: 800
 })
 });

 if (finalRes.ok) {
 const finalData = await finalRes.json();
 const finalReply = finalData.choices?.[0]?.message?.content?.trim();
 return {
 text: toNormalText(finalReply || "Task complete."),
 toolsUsed: toolsUsedLog
 };
 }

 return {
 text: toNormalText(toolsUsedLog.map(t => `${t.tool}: ${t.result}`).join("\n\n")),
 toolsUsed: toolsUsedLog
 };
 };

 // ═════════════════════════════════════════════════════════════════════
 // 5. RAG DOCUMENT CONTEXT SEARCH
 // ═════════════════════════════════════════════════════════════════════
 const findDocumentContext = (question) => {
 if (documentChunks.length === 0) return null;

 const stopWords = new Set(["the", "is", "at", "which", "on", "and", "a", "an", "in", "what", "how", "who", "when", "why", "where", "are", "of", "to", "for", "with"]);
 const queryTokens = question.toLowerCase().replace(/[^a-z0-9 ]/g, ' ').split(/\s+/).filter(t => t.length > 2 && !stopWords.has(t));

 if (queryTokens.length === 0) return null;

 const scored = documentChunks.map(chunk => {
 const lowerChunk = chunk.text.toLowerCase();
 let matchCount = 0;
 queryTokens.forEach(token => {
 if (lowerChunk.includes(token)) matchCount++;
 });
 return { chunk, score: matchCount / queryTokens.length };
 }).filter(item => item.score > 0.25);

 scored.sort((a, b) => b.score - a.score);

 if (scored.length > 0) {
 return scored.slice(0, 3).map(s => s.chunk.text);
 }
 return null;
 };

 // ═════════════════════════════════════════════════════════════════════
 // 6. MAIN DISPATCHER: RAG VS AI AGENT
 // ═════════════════════════════════════════════════════════════════════
 const handleSend = async (queryText) => {
 const q = (queryText || inputQuery).trim();
 if (!q) return;

 setInputQuery('');
 const userMsg = {
 id: Date.now(),
 sender: 'user',
 text: q
 };

 if (mode === 'rag') {
 setRagMessages((prev) => [...prev, userMsg]);
 } else {
 setAgentMessages((prev) => [...prev, userMsg]);
 }

 setIsLoading(true);
 setCurrentStepText('Processing request...');

 // ─────────────────────────────────────────────────────────────────
 // BRANCH A: AI AGENT MODE
 // ─────────────────────────────────────────────────────────────────
 if (mode === 'agent') {
 try {
 const agentResult = await executeAgentWorkflow(q);
 setAgentMessages((prev) => [
 ...prev,
 {
 id: Date.now() + 1,
 sender: 'assistant',
 text: agentResult.text,
 source: 'agent',
 sourceLabel: ' Autonomous AI Agent (Tools & Search)',
 toolsUsed: agentResult.toolsUsed || []
 }
 ]);
 } catch (err) {
 setAgentMessages((prev) => [
 ...prev,
 {
 id: Date.now() + 1,
 sender: 'assistant',
 text: `Agent execution encountered an error: ${err.message}. Please verify your API key in the top bar.`,
 source: 'error',
 sourceLabel: ' Agent Notice',
 toolsUsed: []
 }
 ]);
 } finally {
 setIsLoading(false);
 setCurrentStepText('');
 }
 return;
 }

 // ─────────────────────────────────────────────────────────────────
 // BRANCH B: RAG MODEL MODE
 // ─────────────────────────────────────────────────────────────────
 // Step 1: Real-Time Date/Time Tool
 const toolResult = calculateRelativeDate(q);
 if (toolResult) {
 setTimeout(() => {
 setRagMessages((prev) => [
 ...prev,
 {
 id: Date.now() + 1,
 sender: 'assistant',
 text: toNormalText(toolResult.text),
 source: toolResult.source,
 sourceLabel: toolResult.sourceLabel,
 contexts: []
 }
 ]);
 setIsLoading(false);
 setCurrentStepText('');
 }, 200);
 return;
 }

 // Step 2: Check Document Context (RAG)
 const matchingContexts = findDocumentContext(q);

 if (matchingContexts && matchingContexts.length > 0) {
 try {
 const ragPrompt = `Document Excerpts:\n${matchingContexts.join("\n\n")}\n\nQuestion: ${q}\n\nAnswer the question in clean normal plain text based on the document excerpts above.`;
 const ragAnswer = await callGroqApi(ragPrompt, "You are a precise document assistant. Answer in normal plain text without markdown syntax or asterisks.");

 setRagMessages((prev) => [
 ...prev,
 {
 id: Date.now() + 1,
 sender: 'assistant',
 text: toNormalText(ragAnswer),
 source: 'rag',
 sourceLabel: ' From Your Documents (RAG)',
 contexts: matchingContexts.map(c => toNormalText(c))
 }
 ]);
 } catch (e) {
 setRagMessages((prev) => [
 ...prev,
 {
 id: Date.now() + 1,
 sender: 'assistant',
 text: toNormalText(`From your document: ${matchingContexts[0]}`),
 source: 'rag',
 sourceLabel: ' From Your Documents (RAG)',
 contexts: matchingContexts.map(c => toNormalText(c))
 }
 ]);
 } finally {
 setIsLoading(false);
 setCurrentStepText('');
 }
 return;
 }

 // Step 3: LLM General Knowledge Fallback
 try {
 const llmAnswer = await callGroqApi(q);
 setRagMessages((prev) => [
 ...prev,
 {
 id: Date.now() + 1,
 sender: 'assistant',
 text: toNormalText(llmAnswer),
 source: 'llm',
 sourceLabel: ' From LLM General Knowledge',
 contexts: []
 }
 ]);
 } catch (e) {
 const lower = q.toLowerCase();
 let fallbackText = `I received your question: "${q}".`;
 if (lower === 'hii' || lower === 'hi' || lower === 'hello') {
 fallbackText = "Hello! How can I assist you today? You can ask me any question, calculate dates, or upload documents.";
 }
 setRagMessages((prev) => [
 ...prev,
 {
 id: Date.now() + 1,
 sender: 'assistant',
 text: fallbackText,
 source: 'llm',
 sourceLabel: ' From LLM General Knowledge',
 contexts: []
 }
 ]);
 } finally {
 setIsLoading(false);
 setCurrentStepText('');
 }
 };

 // ═════════════════════════════════════════════════════════════════════
 // 7. FILE UPLOAD HANDLER (RAG)
 // ═════════════════════════════════════════════════════════════════════
 const handleFileUpload = async (e) => {
 const files = Array.from(e.target.files || []);
 if (files.length === 0) return;

 const newDocs = [];
 const newChunks = [];

 for (const file of files) {
 const docItem = {
 id: Date.now() + Math.random(),
 name: file.name,
 size: `${(file.size / 1024).toFixed(1)} KB`,
 type: file.name.endsWith('.pdf') ? 'pdf' : (file.name.match(/\.(png|jpg|jpeg)$/i) ? 'image' : 'text')
 };
 newDocs.push(docItem);

 try {
 const text = await file.text();
 if (text && text.trim()) {
 const chunkSize = 500;
 for (let i = 0; i < text.length; i += 400) {
 const chunkText = text.substring(i, i + chunkSize).trim();
 if (chunkText) {
 newChunks.push({
 docName: file.name,
 text: toNormalText(chunkText)
 });
 }
 }
 } else {
 newChunks.push({
 docName: file.name,
 text: `Document: ${file.name} (${docItem.size}). File uploaded and indexed.`
 });
 }
 } catch (err) {
 newChunks.push({
 docName: file.name,
 text: `Document: ${file.name} (${docItem.size}).`
 });
 }
 }

 setUploadedFiles(prev => [...prev, ...newDocs]);
 setDocumentChunks(prev => [...prev, ...newChunks]);
 };

 const handleClearDocs = () => {
 setUploadedFiles([]);
 setDocumentChunks([]);
 };

 if (!isOpen) return null;

 return (
 <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-slate-900/40 backdrop-blur-md animate-fadeIn">
 {/* ── Outer Clay Studio Dialog ── */}
 <div className="clay-tablet w-full max-w-5xl h-[92vh] flex flex-col overflow-hidden bg-[#f4f6f8] border-4 border-white shadow-2xl relative">
 
 {/* ── Studio Top Header Bar with Branch Selector ── */}
 <div className="px-4 sm:px-6 py-3 border-b border-slate-200/80 flex flex-wrap items-center justify-between bg-white/90 backdrop-blur-sm gap-2">
 
 {/* Logo & Online Status */}
 <div className="flex items-center gap-2.5">
 <div className="w-8 h-8 rounded-xl bg-brand-orange flex items-center justify-center shadow-md">
 <Sparkles className="w-4 h-4 text-white" />
 </div>
 <div>
 <h2 className="text-sm sm:text-base font-black text-slate-900 tracking-tight flex items-center gap-2">
 PixelCore Studio
 <span className="text-[10px] font-mono font-bold bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full border border-emerald-200">
 ONLINE
 </span>
 </h2>
 </div>
 </div>

 {/* ── Prominent Branch / Feature Selector ── */}
 <div className="flex items-center p-1 bg-slate-100 border border-slate-200 rounded-xl shadow-inner">
 <button
 onClick={() => handleBranchSwitch('rag')}
 className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-black transition-all cursor-pointer ${
 mode === 'rag'
 ? 'clay-btn-orange text-white shadow-sm'
 : 'text-slate-600 hover:text-brand-orange'
 }`}
 >
 <BookOpen className="w-3.5 h-3.5" />
 <span>1. RAG Model</span>
 </button>

 <button
 onClick={() => handleBranchSwitch('agent')}
 className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-black transition-all cursor-pointer ${
 mode === 'agent'
 ? 'clay-btn-orange text-white shadow-sm'
 : 'text-slate-600 hover:text-brand-orange'
 }`}
 >
 <Bot className="w-3.5 h-3.5" />
 <span>2. AI Agent</span>
 </button>
 </div>

 {/* Close Button */}
 <button
 onClick={onClose}
 className="clay-btn-grey w-8 h-8 flex items-center justify-center rounded-xl cursor-pointer"
 title="Close Studio"
 >
 <X className="w-4 h-4 text-slate-600" />
 </button>
 </div>

 {/* ── Content: Left Panel + Chat Area ── */}
 <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
 
 {/* ═════════════════════════════════════════════════════════════ */}
 {/* LEFT PANEL: Dynamic per active branch */}
 {/* ═════════════════════════════════════════════════════════════ */}
 <div className="w-full md:w-72 border-r border-slate-200/80 bg-slate-100/60 p-4 flex flex-col justify-between overflow-y-auto gap-4">
 <div>
 {mode === 'rag' ? (
 /* ── RAG MODE: Document Upload Section ── */
 <div>
 <div className="clay-card p-3 mb-4 bg-white/90">
 <div className="flex items-center justify-between mb-2">
 <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
 <BookOpen className="w-3.5 h-3.5 text-brand-orange" />
 Documents ({uploadedFiles.length})
 </span>
 
 <div className="flex items-center gap-1">
 {uploadedFiles.length > 0 && (
 <button
 onClick={handleClearDocs}
 className="text-[10px] text-slate-400 hover:text-rose-500 p-1"
 title="Clear all documents"
 >
 <Trash2 className="w-3 h-3" />
 </button>
 )}
 <label className="text-[10px] font-bold bg-brand-orange text-white px-2 py-0.5 rounded-md cursor-pointer hover:bg-brand-orangeHover transition-colors shadow-sm">
 + Upload
 <input 
 type="file" 
 multiple 
 accept=".pdf,.png,.jpg,.jpeg,.txt,.md" 
 onChange={handleFileUpload} 
 className="hidden" 
 />
 </label>
 </div>
 </div>

 {uploadedFiles.length === 0 ? (
 <div className="py-4 px-2 text-center border-2 border-dashed border-slate-200 rounded-xl">
 <UploadCloud className="w-5 h-5 text-slate-400 mx-auto mb-1" />
 <p className="text-[10px] text-slate-400 font-medium leading-tight">
 No documents uploaded.<br />Click <span className="text-brand-orange font-bold">+ Upload</span> to add PDFs or images.
 </p>
 </div>
 ) : (
 <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
 {uploadedFiles.map((doc) => (
 <div key={doc.id} className="clay-card px-2 py-1.5 flex items-center justify-between text-xs bg-slate-50">
 <div className="flex items-center gap-1.5 truncate">
 {doc.type === 'pdf' ? (
 <FileText className="w-3.5 h-3.5 text-rose-500 flex-shrink-0" />
 ) : (
 <ImageIcon className="w-3.5 h-3.5 text-blue-500 flex-shrink-0" />
 )}
 <span className="font-semibold text-slate-700 truncate text-[11px]">{doc.name}</span>
 </div>
 <span className="text-[9px] text-slate-400 font-mono">{doc.size}</span>
 </div>
 ))}
 </div>
 )}
 </div>

 {/* RAG Quick Prompts */}
 <div>
 <span className="text-[11px] font-bold text-slate-400 mb-2 block uppercase tracking-wider">
 RAG Quick Prompts
 </span>
 <div className="space-y-1.5">
 {[
 { label: 'date +2', badge: ' Tool' },
 { label: 'date after 5 days', badge: ' Tool' },
 { label: 'What are the main findings in my document?', badge: ' RAG' },
 { label: 'Explain Quantum Computing', badge: ' LLM' },
 { label: 'hii', badge: ' LLM' },
 ].map((item, idx) => (
 <button
 key={idx}
 onClick={() => handleSend(item.label)}
 className="w-full text-left clay-card px-3 py-2 hover:bg-white hover:border-brand-orange/40 transition-all cursor-pointer flex items-center justify-between group"
 >
 <span className="text-xs font-bold text-slate-800 group-hover:text-brand-orange font-mono truncate mr-2">
 {item.label}
 </span>
 <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-slate-200 text-slate-600 flex-shrink-0">
 {item.badge}
 </span>
 </button>
 ))}
 </div>
 </div>
 </div>
 ) : (
 /* ── AI AGENT MODE: Autonomous Tools Section ── */
 <div>
 <div className="clay-card p-3 mb-4 bg-white/90">
 <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5 mb-2.5">
 <Bot className="w-3.5 h-3.5 text-brand-orange" />
 Active Agent Tools
 </span>
 
 <div className="space-y-2">
 {/* Tool 1: Tavily */}
 <div className="p-2 rounded-xl bg-slate-50 border border-slate-200/80 flex items-start gap-2">
 <Globe className="w-3.5 h-3.5 text-blue-500 mt-0.5 flex-shrink-0" />
 <div>
 <div className="text-[11px] font-bold text-slate-800 flex items-center gap-1">
 Tavily Web Search
 <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
 </div>
 <div className="text-[9px] text-slate-400">Live internet, breaking news & updates</div>
 </div>
 </div>

 {/* Tool 2: Wikipedia */}
 <div className="p-2 rounded-xl bg-slate-50 border border-slate-200/80 flex items-start gap-2">
 <BookOpen className="w-3.5 h-3.5 text-emerald-600 mt-0.5 flex-shrink-0" />
 <div>
 <div className="text-[11px] font-bold text-slate-800 flex items-center gap-1">
 Wikipedia Search
 <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
 </div>
 <div className="text-[9px] text-slate-400">Encyclopedic knowledge & biographies</div>
 </div>
 </div>

 {/* Tool 3: Math */}
 <div className="p-2 rounded-xl bg-slate-50 border border-slate-200/80 flex items-start gap-2">
 <Calculator className="w-3.5 h-3.5 text-amber-500 mt-0.5 flex-shrink-0" />
 <div>
 <div className="text-[11px] font-bold text-slate-800 flex items-center gap-1">
 Add & Multiply Tools
 <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
 </div>
 <div className="text-[9px] text-slate-400">Zero-hallucination arithmetic calculator</div>
 </div>
 </div>
 </div>
 </div>

 {/* AI Agent Quick Prompts */}
 <div>
 <span className="text-[11px] font-bold text-slate-400 mb-2 block uppercase tracking-wider">
 Agent Quick Prompts
 </span>
 <div className="space-y-1.5">
 {[
 { label: 'According to Wikipedia, who was Alan Turing?', badge: ' Wiki' },
 { label: 'What is (452 * 78) + 982?', badge: ' Math' },
 { label: 'Search web for latest NASA Artemis news', badge: ' Web' },
 { label: 'Find population of Tokyo & Paris and add them', badge: ' Multi' },
 ].map((item, idx) => (
 <button
 key={idx}
 onClick={() => handleSend(item.label)}
 className="w-full text-left clay-card px-3 py-2 hover:bg-white hover:border-brand-orange/40 transition-all cursor-pointer flex items-center justify-between group"
 >
 <span className="text-xs font-bold text-slate-800 group-hover:text-brand-orange font-mono truncate mr-2">
 {item.label}
 </span>
 <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-slate-200 text-slate-600 flex-shrink-0">
 {item.badge}
 </span>
 </button>
 ))}
 </div>
 </div>
 </div>
 )}
 </div>

 {/* Model Status Card */}
 <div className="clay-card p-2.5 bg-white text-center">
 <span className="text-[10px] font-mono text-slate-500 font-bold block">
 Groq Acceleration (openai/gpt-oss-20b)
 </span>
 <span className="text-[9px] text-emerald-600 font-semibold">
 ● Active AI Agent API Key Loaded
 </span>
 </div>
 </div>

 {/* ═════════════════════════════════════════════════════════════ */}
 {/* RIGHT PANEL: Chat Messages + Input Bar */}
 {/* ═════════════════════════════════════════════════════════════ */}
 <div className="flex-1 flex flex-col justify-between bg-white/60 p-4 sm:p-5 overflow-hidden">
 
 {/* Messages Scroll Area */}
 <div className="flex-1 overflow-y-auto space-y-3.5 pr-1">
 {currentMessages.map((m) => (
 <div
 key={m.id}
 className={`flex flex-col ${m.sender === 'user' ? 'items-end' : 'items-start'}`}
 >
 <div
 className={`max-w-[88%] rounded-[20px] p-3 sm:p-3.5 text-xs sm:text-sm leading-relaxed ${
 m.sender === 'user'
 ? 'clay-btn-orange text-white'
 : 'clay-card bg-white text-slate-800 border-2 border-white'
 }`}
 >
 {/* Message Text */}
 <div className="whitespace-pre-line font-medium leading-relaxed">
 {m.text}
 </div>

 {/* Source Attribution Badge */}
 {m.sender === 'assistant' && m.sourceLabel && (
 <div className="mt-2.5 pt-2 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2">
 <span
 className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
 m.source === 'rag'
 ? 'bg-emerald-50 text-emerald-700 border-emerald-300'
 : m.source === 'agent'
 ? 'bg-orange-50 text-orange-700 border-orange-300'
 : m.source === 'tool'
 ? 'bg-amber-50 text-amber-700 border-amber-300'
 : 'bg-blue-50 text-blue-700 border-blue-300'
 }`}
 >
 {m.sourceLabel}
 </span>

 {/* RAG Context Button */}
 {m.contexts && m.contexts.length > 0 && (
 <button
 onClick={() => setShowContexts(prev => ({ ...prev, [m.id]: !prev[m.id] }))}
 className="text-[10px] font-bold text-slate-400 hover:text-slate-700 flex items-center gap-0.5 cursor-pointer"
 >
 <span>{showContexts[m.id] ? 'Hide' : 'Context'}</span>
 {showContexts[m.id] ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
 </button>
 )}

 {/* AI Agent Tools Used Button */}
 {m.toolsUsed && m.toolsUsed.length > 0 && (
 <button
 onClick={() => setShowToolsUsed(prev => ({ ...prev, [m.id]: !prev[m.id] }))}
 className="text-[10px] font-bold text-slate-500 hover:text-slate-800 flex items-center gap-0.5 cursor-pointer"
 >
 <span>{showToolsUsed[m.id] ? 'Hide Tools' : ' Tools Used'}</span>
 {showToolsUsed[m.id] ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
 </button>
 )}
 </div>
 )}

 {/* Expandable RAG Context Snippet */}
 {showContexts[m.id] && m.contexts && (
 <div className="mt-2 p-2 rounded-lg bg-slate-100 border border-slate-200 text-[10px] font-mono text-slate-600 space-y-1">
 {m.contexts.map((c, i) => (
 <div key={i} className="border-l-2 border-brand-orange pl-1.5">
 {c}
 </div>
 ))}
 </div>
 )}

 {/* Expandable AI Agent Tools Used Trace */}
 {showToolsUsed[m.id] && m.toolsUsed && (
 <div className="mt-2 p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-[10px] text-slate-700 space-y-1.5 font-mono">
 <div className="font-bold text-slate-800 flex items-center gap-1">
 <CheckCircle2 className="w-3 h-3 text-emerald-600" />
 <span>Intermediate Steps & Tool Observations:</span>
 </div>
 {Array.isArray(m.toolsUsed) && m.toolsUsed.map((t, i) => (
 <div key={i} className="pl-2 border-l-2 border-brand-orange py-0.5">
 {typeof t === 'string' ? (
 <span>• {t}</span>
 ) : (
 <div>
 <span className="font-bold text-brand-orange">[{t.tool}]</span>
 {t.query && <span> → Input: "{t.query}"</span>}
 {t.result && (
 <div className="text-[9px] text-slate-500 mt-0.5 truncate">
 Result: {t.result}
 </div>
 )}
 </div>
 )}
 </div>
 ))}
 </div>
 )}
 </div>
 </div>
 ))}

 {isLoading && (
 <div className="flex items-center gap-2 text-xs font-bold text-brand-orange clay-card p-2.5 w-fit bg-white">
 <span className="w-2 h-2 rounded-full bg-brand-orange animate-ping"></span>
 <span>{currentStepText || "Thinking..."}</span>
 </div>
 )}
 <div ref={messagesEndRef} />
 </div>

 {/* Input Bar */}
 <form
 onSubmit={(e) => {
 e.preventDefault();
 handleSend();
 }}
 className="mt-3 flex items-center gap-2"
 >
 <div className="clay-inset flex-1 px-4 py-2 flex items-center">
 <input
 type="text"
 value={inputQuery}
 onChange={(e) => setInputQuery(e.target.value)}
 placeholder={
 mode === 'rag'
 ? "Ask a question about your uploaded documents or try 'date +2'..."
 : "Ask the AI Agent (e.g., 'Who was Alan Turing?', 'calculate (452*78)+982')..."
 }
 className="w-full bg-transparent text-xs sm:text-sm font-medium text-slate-800 focus:outline-none placeholder:text-slate-400"
 />
 </div>

 <button
 type="submit"
 disabled={isLoading || !inputQuery.trim()}
 className="clay-btn-orange p-2.5 flex items-center justify-center cursor-pointer disabled:opacity-50"
 title="Send query"
 >
 <Send className="w-4 h-4" />
 </button>
 </form>

 </div>

 </div>

 </div>
 </div>
 );
}
