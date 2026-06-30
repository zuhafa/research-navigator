import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Copy, Share2, FileText, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export default function Report() {
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const cached = localStorage.getItem('current_report');
    if (cached) {
      setReport(JSON.parse(cached));
    }
  }, []);

  if (!report) {
    return (
      <div className="min-h-screen bg-bg text-primaryText flex flex-col items-center justify-center p-6 text-center">
        <FileText className="w-16 h-16 text-primaryAccent mb-4 animate-bounce" />
        <h2 className="text-xl font-bold mb-2">No Active Research Session</h2>
        <p className="text-sm text-secondaryText mb-6 max-w-sm">
          Please run a research query in the workspace first to generate the report.
        </p>
        <button
          onClick={() => navigate('/workspace')}
          className="px-6 py-2.5 rounded-xl bg-primaryAccent hover:opacity-90 transition text-sm font-medium"
        >
          Go to Workspace
        </button>
      </div>
    );
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(report.raw);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-bg text-primaryText p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Back header */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => navigate('/workspace')}
            className="flex items-center gap-2 text-sm text-secondaryText hover:text-white transition"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Workspace
          </button>

          <div className="flex gap-2">
            <button
              onClick={handleCopy}
              className="px-4 py-2 rounded-xl bg-white/5 border border-borderColor hover:bg-white/10 text-xs font-semibold flex items-center gap-1.5 transition text-white"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-success" /> : <Copy className="w-3.5 h-3.5" />}
              {copied ? 'Copied!' : 'Copy Markdown'}
            </button>
            <button
              onClick={() => alert('Mentorship report sharing link generated and copied to clipboard!')}
              className="px-4 py-2 rounded-xl bg-white/5 border border-borderColor hover:bg-white/10 text-xs font-semibold flex items-center gap-1.5 transition text-white"
            >
              <Share2 className="w-3.5 h-3.5" />
              Share Report
            </button>
          </div>
        </div>

        {/* Notebook layout */}
        <div className="bg-bgSecondary/40 border border-borderColor rounded-3xl p-8 sm:p-12 shadow-2xl relative">
          <div className="absolute top-0 right-12 w-24 h-24 bg-primaryAccent/5 rounded-full blur-xl" />
          
          <div className="border-b border-borderColor/60 pb-8 mb-8 flex items-center justify-between">
            <div className="space-y-2">
              <span className="text-xs font-semibold text-primaryAccent uppercase tracking-widest">Mentorship Dossier</span>
              <h2 className="text-3xl font-extrabold text-white tracking-tight">Mentorship Report Summary</h2>
            </div>
            <FileText className="w-10 h-10 text-secondaryText/40" />
          </div>

          <div className="text-sm leading-relaxed text-secondaryText markdown-content prose prose-invert max-w-none space-y-6">
            <ReactMarkdown>{report.raw}</ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  );
}
