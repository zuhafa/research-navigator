import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Send, Bot, User, CheckCircle2, Loader2, Play, AlertTriangle, 
  ArrowRight, ShieldCheck, HelpCircle, Check, ListChecks, GraduationCap, History, Trash2
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { parseReport } from '../utils/reportParser';

export default function Workspace() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [statusText, setStatusText] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState('');
  const [activeInvocationId, setActiveInvocationId] = useState('');
  const [savedSessions, setSavedSessions] = useState([]);
  
  // Timeline/status tracking states
  const [timeline, setTimeline] = useState([
    { id: 'domain', label: 'Reading Paper & Domain Classifying', status: 'idle' }, // idle, active, done
    { id: 'prereqs', label: 'Checking Prerequisites', status: 'idle' },
    { id: 'datasets', label: 'Finding Datasets Details', status: 'idle' },
    { id: 'complexity', label: 'Estimating Build Complexity', status: 'idle' },
    { id: 'roadmap', label: 'Generating Learning Roadmap', status: 'idle' },
    { id: 'readiness', label: 'Evaluating Readiness Score', status: 'idle' },
  ]);

  const [humanReviewPaused, setHumanReviewPaused] = useState(false);
  const [pendingReport, setPendingReport] = useState('');
  const [feedback, setFeedback] = useState('');
  const [submittingFeedback, setSubmittingFeedback] = useState(false);
  const chatEndRef = useRef(null);

  const examplePrompts = [
    'Vision Transformers in Medical Imaging',
    'CNNs in Plant Disease Classification',
    'Graph Neural Networks for Drug Discovery',
    'Explain Self-Supervised Learning in Speech Recognition'
  ];

  // Load saved sessions on mount
  useEffect(() => {
    const loaded = localStorage.getItem('navigator_sessions');
    if (loaded) {
      setSavedSessions(JSON.parse(loaded));
    }
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading, timeline]);

  // Helper to save session to localStorage history
  const saveSessionToHistory = (sessionId, firstQuery, updatedMessages, reportText) => {
    const loaded = localStorage.getItem('navigator_sessions');
    let list = loaded ? JSON.parse(loaded) : [];
    
    const index = list.findIndex(s => s.id === sessionId);
    const sessionObj = {
      id: sessionId,
      query: firstQuery,
      messages: updatedMessages,
      report: reportText,
      timestamp: new Date().toISOString()
    };
    
    if (index > -1) {
      list[index] = sessionObj;
    } else {
      list.unshift(sessionObj);
    }
    
    localStorage.setItem('navigator_sessions', JSON.stringify(list));
    setSavedSessions(list);
  };

  // Initializing new session
  const createNewSession = async () => {
    try {
      const res = await fetch('http://localhost:18081/apps/app/users/user/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await res.json();
      setActiveSessionId(data.id);
      return data.id;
    } catch (e) {
      console.error('Failed to create session:', e);
      const fallbackId = 'session-' + Math.random().toString(36).substr(2, 9);
      setActiveSessionId(fallbackId);
      return fallbackId;
    }
  };

  const handlePromptSelect = (prompt) => {
    setQuery(prompt);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim() || loading) return;

    const userMessage = query;
    setQuery('');
    setLoading(true);
    setHumanReviewPaused(false);
    
    const newMessages = [...messages, { role: 'user', content: userMessage }];
    setMessages(newMessages);
    
    // Reset timeline
    setTimeline(prev => prev.map(t => ({ ...t, status: 'idle' })));

    let sessionId = activeSessionId;
    if (!sessionId) {
      sessionId = await createNewSession();
    }

    // Save initial session state
    const titleQuery = messages.length === 0 ? userMessage : (savedSessions.find(s => s.id === sessionId)?.query || userMessage);
    saveSessionToHistory(sessionId, titleQuery, newMessages, pendingReport);

    try {
      const response = await fetch('http://localhost:18081/run_sse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          app_name: 'app',
          user_id: 'user',
          session_id: sessionId,
          new_message: {
            role: 'user',
            parts: [{ text: userMessage }]
          },
          streaming: true
        })
      });

      if (!response.ok) {
        throw new Error('API request failed');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';
      let currentText = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop();

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.replace('data: ', '').trim();
            if (!dataStr) continue;

            try {
              const event = JSON.parse(dataStr);
              
              if (event.invocation_id) {
                setActiveInvocationId(event.invocation_id);
              }

              // Update timeline status based on node execution / tool calls
              if (event.node_name === 'orchestrator') {
                const calls = event.get_function_calls || [];
                
                if (calls.includes('get_research_domain')) {
                  updateTimeline('domain', 'active');
                }
                if (calls.includes('check_prerequisites')) {
                  updateTimeline('domain', 'done');
                  updateTimeline('prereqs', 'active');
                }
                if (calls.includes('check_dataset_spec')) {
                  updateTimeline('prereqs', 'done');
                  updateTimeline('datasets', 'active');
                }
                if (calls.includes('estimate_complexity')) {
                  updateTimeline('datasets', 'done');
                  updateTimeline('complexity', 'active');
                }
                if (calls.includes('get_learning_path')) {
                  updateTimeline('complexity', 'done');
                  updateTimeline('roadmap', 'active');
                }
                if (calls.includes('get_readiness_rules') || calls.includes('get_project_templates')) {
                  updateTimeline('roadmap', 'done');
                  updateTimeline('readiness', 'active');
                }
              }

              if (event.content && event.content.parts) {
                const textPart = event.content.parts.find(p => p.text);
                if (textPart) {
                  currentText += textPart.text;
                }
              }

              if (event.node_name === 'human_review' && event.get_function_calls?.includes('adk_request_input')) {
                setHumanReviewPaused(true);
                setTimeline(prev => prev.map(t => ({ ...t, status: 'done' })));
              }
            } catch (err) {}
          }
        }
      }

      setLoading(false);
      
      if (currentText) {
        setPendingReport(currentText);
        const parsed = parseReport(currentText);
        localStorage.setItem('current_report', JSON.stringify(parsed));
        
        // Save final report inside list history
        saveSessionToHistory(sessionId, titleQuery, [...newMessages, { role: 'model', content: 'Report generated successfully. You can review the sections now.' }], currentText);
      }

    } catch (err) {
      console.error(err);
      setLoading(false);
      const errMessages = [...newMessages, { 
        role: 'model', 
        content: '⚠️ Failed to connect to local ADK backend server. Please verify the backend uvicorn server is running on port 18081.' 
      }];
      setMessages(errMessages);
      saveSessionToHistory(sessionId, titleQuery, errMessages, pendingReport);
    }
  };

  const updateTimeline = (id, status) => {
    setTimeline(prev => prev.map(item => {
      if (item.id === id) {
        return { ...item, status };
      }
      return item;
    }));
  };

  // Human Review Actions
  const handleApprove = async () => {
    setSubmittingFeedback(true);
    try {
      await fetch('http://localhost:18081/run_sse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          app_name: 'app',
          user_id: 'user',
          session_id: activeSessionId,
          invocation_id: activeInvocationId,
          new_message: {
            role: 'user',
            parts: [{
              function_response: {
                name: 'adk_request_input',
                id: 'approval',
                response: { result: 'approve' }
              }
            }]
          },
          streaming: true
        })
      });

      setHumanReviewPaused(false);
      const approveMessages = [...messages, { 
        role: 'model', 
        content: '🎉 **Mentorship Report Finalized & Approved!** You can now explore the structured roadmap and dashboard analytics.' 
      }];
      setMessages(approveMessages);
      
      const title = savedSessions.find(s => s.id === activeSessionId)?.query || "Mentorship Session";
      saveSessionToHistory(activeSessionId, title, approveMessages, pendingReport);
    } catch (e) {
      console.error(e);
    }
    setSubmittingFeedback(false);
  };

  const handleFeedbackSubmit = async (e) => {
    e.preventDefault();
    if (!feedback.trim()) return;
    setSubmittingFeedback(true);

    const userFeedback = feedback;
    setFeedback('');

    try {
      await fetch('http://localhost:18081/run_sse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          app_name: 'app',
          user_id: 'user',
          session_id: activeSessionId,
          invocation_id: activeInvocationId,
          new_message: {
            role: 'user',
            parts: [{
              function_response: {
                name: 'adk_request_input',
                id: 'approval',
                response: { result: userFeedback }
              }
            }]
          },
          streaming: true
        })
      });

      setHumanReviewPaused(false);
      setMessages(prev => [...prev, { role: 'user', content: `Adjust report: ${userFeedback}` }]);
      
      // Update history
      const title = savedSessions.find(s => s.id === activeSessionId)?.query || "Mentorship Session";
      saveSessionToHistory(activeSessionId, title, [...messages, { role: 'user', content: `Adjust report: ${userFeedback}` }], pendingReport);
    } catch (e) {
      console.error(e);
    }
    setSubmittingFeedback(false);
  };

  // Load an existing session from sidebar
  const loadSavedSession = (session) => {
    setActiveSessionId(session.id);
    setMessages(session.messages || []);
    setPendingReport(session.report || '');
    setHumanReviewPaused(false);
    
    if (session.report) {
      const parsed = parseReport(session.report);
      localStorage.setItem('current_report', JSON.stringify(parsed));
    }
  };

  const deleteSession = (e, sessionId) => {
    e.stopPropagation();
    const loaded = localStorage.getItem('navigator_sessions');
    if (loaded) {
      let list = JSON.parse(loaded);
      list = list.filter(s => s.id !== sessionId);
      localStorage.setItem('navigator_sessions', JSON.stringify(list));
      setSavedSessions(list);
      
      if (activeSessionId === sessionId) {
        setActiveSessionId('');
        setMessages([]);
        setPendingReport('');
        localStorage.removeItem('current_report');
      }
    }
  };


  return (
    <div className="flex h-screen bg-bg text-primaryText overflow-hidden">
      {/* Sidebar */}
      <div className="w-80 bg-bgSecondary border-r border-borderColor flex flex-col justify-between p-6">
        <div className="flex flex-col gap-6 overflow-hidden">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/')}>
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-primaryAccent to-secondaryAccent flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-lg">Research Navigator</span>
          </div>

          <button
            onClick={async () => {
              await createNewSession();
              setMessages([]);
              setTimeline(prev => prev.map(t => ({ ...t, status: 'idle' })));
              setHumanReviewPaused(false);
              setPendingReport('');
            }}
            className="w-full py-3 rounded-xl border border-borderColor hover:bg-white/5 transition text-sm font-medium flex items-center justify-center gap-2"
          >
            + New Mentorship Chat
          </button>

          {/* Saved Sessions list */}
          <div className="flex flex-col gap-2 overflow-y-auto mt-2 max-h-[45vh] border-b border-borderColor/40 pb-4">
            <div className="text-xs font-semibold text-secondaryText uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <History className="w-3.5 h-3.5" />
              Recent Sessions
            </div>
            {savedSessions.length === 0 ? (
              <div className="text-xs text-secondaryText italic pl-2">No past sessions saved</div>
            ) : (
              savedSessions.map((s, idx) => (
                <div 
                  key={idx}
                  className={`w-full flex items-center justify-between rounded-xl border p-1 transition group ${activeSessionId === s.id ? 'bg-primaryAccent/10 border-primaryAccent/30' : 'border-transparent hover:bg-white/5'}`}
                >
                  <button
                    onClick={() => loadSavedSession(s)}
                    className={`flex-grow py-1.5 px-2 text-left text-xs truncate transition font-medium ${activeSessionId === s.id ? 'text-white' : 'text-secondaryText hover:text-white'}`}
                  >
                    {s.query}
                  </button>
                  <button
                    onClick={(e) => deleteSession(e, s.id)}
                    className="p-1.5 rounded-lg hover:bg-danger/20 text-secondaryText hover:text-danger opacity-0 group-hover:opacity-100 transition shrink-0 mr-1"
                    title="Delete session"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="flex flex-col gap-4 mt-4">
          <div className="text-xs font-semibold text-secondaryText uppercase tracking-wider">Navigation</div>
          <button 
            disabled={!pendingReport}
            onClick={() => navigate('/dashboard')}
            className={`w-full py-2.5 px-4 rounded-xl text-left text-sm font-medium flex items-center gap-2 transition ${pendingReport ? 'hover:bg-white/5 text-primaryText' : 'opacity-50 cursor-not-allowed text-secondaryText'}`}
          >
            <ListChecks className="w-4 h-4 text-primaryAccent" />
            Analysis Dashboard
          </button>
          <button 
            disabled={!pendingReport}
            onClick={() => navigate('/roadmap')}
            className={`w-full py-2.5 px-4 rounded-xl text-left text-sm font-medium flex items-center gap-2 transition ${pendingReport ? 'hover:bg-white/5 text-primaryText' : 'opacity-50 cursor-not-allowed text-secondaryText'}`}
          >
            <GraduationCap className="w-4 h-4 text-secondaryAccent" />
            Learning Roadmap
          </button>
          <button 
            disabled={!pendingReport}
            onClick={() => navigate('/report')}
            className={`w-full py-2.5 px-4 rounded-xl text-left text-sm font-medium flex items-center gap-2 transition ${pendingReport ? 'hover:bg-white/5 text-primaryText' : 'opacity-50 cursor-not-allowed text-secondaryText'}`}
          >
            <Bot className="w-4 h-4 text-success" />
            Mentorship Report
          </button>
        </div>
      </div>

      {/* Main Area */}
      <div className="flex-grow flex flex-col justify-between bg-bg relative">
        {/* Messages */}
        <div className="flex-grow overflow-y-auto p-8 space-y-6">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-center max-w-lg mx-auto">
              <Bot className="w-16 h-16 text-primaryAccent mb-6 animate-pulse" />
              <h2 className="text-2xl font-bold mb-3">Welcome to Research Navigator AI</h2>
              <p className="text-sm text-secondaryText mb-8 leading-relaxed">
                Provide a paper topic, abstract, or arXiv link to evaluate readiness, prerequisites, library requirements, and receive a weekly study timeline.
              </p>
              <div className="grid grid-cols-2 gap-3 w-full">
                {examplePrompts.map((p, i) => (
                  <button
                    key={i}
                    onClick={() => handlePromptSelect(p)}
                    className="p-3 text-xs text-left rounded-xl bg-cardBg/30 border border-borderColor hover:border-primaryAccent/30 hover:bg-cardBg/50 transition"
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div key={idx} className={`flex gap-4 max-w-3xl ${msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''}`}>
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-primaryAccent' : 'bg-white/5'}`}>
                {msg.role === 'user' ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-primaryAccent" />}
              </div>
              <div className={`p-4 rounded-2xl text-sm leading-relaxed ${msg.role === 'user' ? 'bg-primaryAccent/10 border border-primaryAccent/20' : 'bg-cardBg/30 border border-borderColor'}`}>
                {msg.content}
              </div>
            </div>
          ))}

          {/* Timeline Loader */}
          {loading && (
            <div className="max-w-md p-6 rounded-2xl bg-cardBg/20 border border-borderColor space-y-4">
              <div className="text-xs font-semibold uppercase tracking-wider text-secondaryText mb-2 flex items-center gap-2">
                <Loader2 className="w-3.5 h-3.5 animate-spin text-primaryAccent" />
                Analyzing Research...
              </div>
              <div className="space-y-3">
                {timeline.map((step, idx) => (
                  <div key={idx} className="flex items-center gap-3 text-sm">
                    {step.status === 'done' ? (
                      <CheckCircle2 className="w-4 h-4 text-success shrink-0" />
                    ) : step.status === 'active' ? (
                      <Loader2 className="w-4 h-4 text-primaryAccent animate-spin shrink-0" />
                    ) : (
                      <div className="w-4 h-4 rounded-full border-2 border-borderColor shrink-0" />
                    )}
                    <span className={step.status === 'active' ? 'text-primaryText font-medium' : 'text-secondaryText'}>
                      {step.label}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Human Review Approval State */}
          {humanReviewPaused && (
            <div className="p-6 rounded-2xl border-2 border-warning/30 bg-warning/5 max-w-2xl space-y-4">
              <div className="flex items-center gap-3">
                <ShieldCheck className="w-6 h-6 text-warning" />
                <h3 className="text-lg font-bold text-white">📋 Report Review Required</h3>
              </div>
              <p className="text-sm text-secondaryText leading-relaxed">
                The AI Research Mentor has generated the initial report. Please review the report using the sidebar navigation tabs. You can approve to finalize or request adjustments below.
              </p>
              <div className="flex gap-4">
                <button
                  disabled={submittingFeedback}
                  onClick={handleApprove}
                  className="px-6 py-2.5 rounded-xl bg-success hover:bg-success/80 text-white font-medium text-sm transition flex items-center gap-2"
                >
                  {submittingFeedback ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
                  Approve and Finalize Report
                </button>
              </div>
              <form onSubmit={handleFeedbackSubmit} className="flex gap-2 border-t border-borderColor pt-4">
                <input
                  type="text"
                  placeholder="Request changes (e.g. Add PyTorch resources, explain ResNet depth)..."
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  disabled={submittingFeedback}
                  className="flex-grow bg-white/5 border border-borderColor rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-warning/50 text-white"
                />
                <button
                  type="submit"
                  disabled={submittingFeedback || !feedback.trim()}
                  className="px-4 py-2 rounded-xl bg-white/5 border border-borderColor hover:bg-white/10 text-white font-medium text-sm transition"
                >
                  Submit Changes
                </button>
              </form>
            </div>
          )}
          
          {/* Approved final links */}
          {pendingReport && !humanReviewPaused && !loading && (
            <div className="p-6 rounded-2xl bg-success/5 border border-success/20 max-w-md flex flex-col gap-4">
              <div className="flex items-center gap-3 text-success">
                <CheckCircle2 className="w-5 h-5" />
                <h4 className="font-bold">Mentorship Session Ready</h4>
              </div>
              <p className="text-xs text-secondaryText leading-relaxed">
                The parsed learning roadmaps, dataset specs, and beginner projects are ready for you. Use the links below to view the interactive sections.
              </p>
              <div className="flex flex-wrap gap-2">
                <button 
                  onClick={() => navigate('/dashboard')}
                  className="px-4 py-2 text-xs font-semibold rounded-xl bg-primaryAccent hover:opacity-90 transition text-white"
                >
                  View Dashboard
                </button>
                <button 
                  onClick={() => navigate('/roadmap')}
                  className="px-4 py-2 text-xs font-semibold rounded-xl bg-secondaryAccent hover:opacity-90 transition text-bg font-bold"
                >
                  Learning Timeline
                </button>
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Input */}
        <div className="p-6 border-t border-borderColor bg-bg">
          <form onSubmit={handleSubmit} className="relative max-w-3xl mx-auto">
            <input
              type="text"
              placeholder="Query paper, paste arXiv URL, or type research topic..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={loading || humanReviewPaused}
              className="w-full bg-bgSecondary border border-borderColor rounded-2xl py-4 pl-6 pr-14 text-sm focus:outline-none focus:border-primaryAccent/50 placeholder:text-secondaryText text-white"
            />
            <button
              type="submit"
              disabled={loading || !query.trim() || humanReviewPaused}
              className="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-xl bg-primaryAccent hover:bg-primaryAccent/80 text-white flex items-center justify-center transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
