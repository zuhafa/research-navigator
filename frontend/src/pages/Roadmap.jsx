import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Clock, GraduationCap, Calendar, CheckCircle2, ChevronRight } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export default function Roadmap() {
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [completedWeeks, setCompletedWeeks] = useState([]);

  useEffect(() => {
    const cached = localStorage.getItem('current_report');
    if (cached) {
      setReport(JSON.parse(cached));
    }
  }, []);

  if (!report) {
    return (
      <div className="min-h-screen bg-bg text-primaryText flex flex-col items-center justify-center p-6 text-center">
        <GraduationCap className="w-16 h-16 text-primaryAccent mb-4 animate-bounce" />
        <h2 className="text-xl font-bold mb-2">No Active Research Session</h2>
        <p className="text-sm text-secondaryText mb-6 max-w-sm">
          Please run a research query in the workspace first to populate the learning roadmap.
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

  const toggleWeekCompleted = (week) => {
    if (completedWeeks.includes(week)) {
      setCompletedWeeks(prev => prev.filter(w => w !== week));
    } else {
      setCompletedWeeks(prev => [...prev, week]);
    }
  };

  const progressPercent = report.learningPlan.length 
    ? Math.round((completedWeeks.length / report.learningPlan.length) * 100)
    : 0;

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
          
          {/* Progress bar */}
          <div className="flex items-center gap-3">
            <span className="text-xs text-secondaryText font-medium">Roadmap Progress: {progressPercent}%</span>
            <div className="w-32 h-2 rounded-full bg-white/5 overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-primaryAccent to-secondaryAccent transition-all duration-300"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>
        </div>

        {/* Header */}
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight mb-2">Personalized Learning Roadmap</h1>
          <p className="text-sm text-secondaryText">
            A customized weekly study timeline crafted to bridge your technical skills with the target research paper methodology.
          </p>
        </div>

        {/* Timeline */}
        <div className="relative border-l border-borderColor/40 ml-4 pl-8 space-y-12 py-4">
          {report.learningPlan.map((week, idx) => {
            const isCompleted = completedWeeks.includes(week.week);
            return (
              <div key={idx} className="relative group">
                {/* Timeline node */}
                <button
                  onClick={() => toggleWeekCompleted(week.week)}
                  className={`absolute left-[-41px] top-1.5 w-6 h-6 rounded-full border-2 bg-bg flex items-center justify-center transition-all ${isCompleted ? 'border-success text-success' : 'border-borderColor text-secondaryText hover:border-primaryAccent'}`}
                >
                  {isCompleted ? <CheckCircle2 className="w-4 h-4" /> : <div className="w-2 h-2 rounded-full bg-borderColor group-hover:bg-primaryAccent transition" />}
                </button>

                {/* Week card */}
                <div className={`p-6 rounded-2xl border bg-cardBg/10 transition-all duration-300 ${isCompleted ? 'border-success/20 bg-success/[0.02]' : 'border-borderColor hover:border-primaryAccent/25 hover:bg-cardBg/20'}`}>
                  <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 mb-4">
                    <span className={`px-3 py-1 rounded-full border text-xs font-semibold uppercase tracking-wider ${isCompleted ? 'bg-success/10 border-success/20 text-success' : 'bg-primaryAccent/10 border-primaryAccent/20 text-primaryAccent'}`}>
                      {week.week}
                    </span>
                    <div className="flex items-center gap-4 text-xs text-secondaryText">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5" />
                        Est. Hours: 10-15h
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3.5 h-3.5" />
                        Target: Week {idx + 1}
                      </span>
                    </div>
                  </div>

                  <div className="text-sm leading-relaxed text-secondaryText markdown-content prose prose-invert max-w-none">
                    <ReactMarkdown>{week.content}</ReactMarkdown>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
