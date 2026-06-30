import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, BookOpen, GraduationCap, Database, 
  Code, Gauge, Lightbulb, ChevronRight, ChevronDown 
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export default function Dashboard() {
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [expandedCard, setExpandedCard] = useState(null);

  useEffect(() => {
    const cached = localStorage.getItem('current_report');
    if (cached) {
      setReport(JSON.parse(cached));
    }
  }, []);

  if (!report) {
    return (
      <div className="min-h-screen bg-bg text-primaryText flex flex-col items-center justify-center p-6 text-center">
        <Gauge className="w-16 h-16 text-primaryAccent mb-4 animate-bounce" />
        <h2 className="text-xl font-bold mb-2">No Active Research Session</h2>
        <p className="text-sm text-secondaryText mb-6 max-w-sm">
          Please run a research query in the workspace first to populate the analysis dashboard.
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

  const cards = [
    { 
      id: 'summary', 
      icon: BookOpen, 
      color: 'text-primaryAccent',
      bg: 'bg-primaryAccent/10',
      title: 'Executive Summary', 
      desc: 'High-level objectives, methodologies, and general outcomes.',
      content: report.summary 
    },
    { 
      id: 'prereqs', 
      icon: GraduationCap, 
      color: 'text-secondaryAccent',
      bg: 'bg-secondaryAccent/10',
      title: 'Prerequisite Analysis', 
      desc: 'Required knowledge base, mathematical structures, and libraries.',
      content: report.prerequisites 
    },
    { 
      id: 'datasets', 
      icon: Database, 
      color: 'text-success',
      bg: 'bg-success/10',
      title: 'Dataset Spec & Details', 
      desc: 'Data dimensions, class counts, access, and public alternatives.',
      content: report.datasets 
    },
    { 
      id: 'complexity', 
      icon: Code, 
      color: 'text-warning',
      bg: 'bg-warning/10',
      title: 'Complexity Assessment', 
      desc: 'Difficulty grade, libraries, hardware recommendations, and build time.',
      content: report.complexity 
    },
    { 
      id: 'projects', 
      icon: Lightbulb, 
      color: 'text-primaryAccent',
      bg: 'bg-primaryAccent/10',
      title: 'Suggested Projects', 
      desc: 'Personalized beginner, intermediate, and advanced project roadmaps.',
      content: report.projects.map(p => `### ${p.title}\n${p.content}`).join('\n\n')
    },
    { 
      id: 'readiness', 
      icon: Gauge, 
      color: 'text-danger',
      bg: 'bg-danger/10',
      title: `Readiness: ${report.readinessScore}/100`, 
      desc: 'Mentorship grade, missing skills, and targeted preparation steps.',
      content: report.readinessExplanation 
    },
  ];

  return (
    <div className="min-h-screen bg-bg text-primaryText p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Back header */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => navigate('/workspace')}
            className="flex items-center gap-2 text-sm text-secondaryText hover:text-white transition"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Workspace
          </button>
          <div className="text-sm text-secondaryText">
            Subject suitability level: <span className="text-warning font-semibold">{report.feasibility.level}</span>
          </div>
        </div>

        {/* Dashboard Header */}
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight mb-2">Research Analysis Dashboard</h1>
          <p className="text-sm text-secondaryText">
            Explore the structural overview of your research topic. Click on any card to view detailed deconstructions.
          </p>
        </div>

        {/* Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cards.map((card, idx) => {
            const isExpanded = expandedCard === card.id;
            return (
              <div
                key={idx}
                className={`rounded-2xl border bg-cardBg/20 border-borderColor hover:border-primaryAccent/20 transition-all duration-300 flex flex-col justify-between p-6 ${isExpanded ? 'md:col-span-2 lg:col-span-3 bg-cardBg/40 border-primaryAccent/30' : ''}`}
              >
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className={`w-10 h-10 rounded-xl ${card.bg} flex items-center justify-center ${card.color}`}>
                      <card.icon className="w-5 h-5" />
                    </div>
                    <button
                      onClick={() => setExpandedCard(isExpanded ? null : card.id)}
                      className="text-secondaryText hover:text-white transition"
                    >
                      {isExpanded ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                    </button>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-bold text-white mb-1">{card.title}</h3>
                    <p className="text-xs text-secondaryText leading-relaxed">{card.desc}</p>
                  </div>
                </div>

                {isExpanded ? (
                  <div className="mt-6 pt-6 border-t border-borderColor/50 text-sm leading-relaxed text-secondaryText markdown-content prose prose-invert max-w-none">
                    <ReactMarkdown>{card.content}</ReactMarkdown>
                  </div>
                ) : (
                  <button
                    onClick={() => setExpandedCard(card.id)}
                    className="mt-6 text-xs font-semibold text-primaryAccent hover:text-secondaryAccent transition text-left flex items-center gap-1"
                  >
                    Expand details
                    <ChevronRight className="w-3 h-3" />
                  </button>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
