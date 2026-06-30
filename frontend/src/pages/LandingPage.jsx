import React from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, GraduationCap, Code, Database, Gauge, Lightbulb, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

export default function LandingPage() {
  const navigate = useNavigate();

  const features = [
    { icon: BookOpen, title: 'Understand Papers', desc: 'Deconstruct complex paper methodology, math equations, and technical terms in plain English.' },
    { icon: GraduationCap, title: 'Learning Roadmaps', desc: 'Generate customized weekly roadmaps covering necessary fundamentals, math calculus, and libraries.' },
    { icon: Code, title: 'Implementation Guidance', desc: 'Assess build difficulty, library dependencies, hardware recommendations, and estimated weeks.' },
    { icon: Database, title: 'Dataset Discovery', desc: 'Query data specifications, sizes, accessibility, and explore alternative public datasets.' },
    { icon: Gauge, title: 'Readiness Assessment', desc: 'Evaluate your technical skills against research complexity and get a quantitative suitability grade.' },
    { icon: Lightbulb, title: 'Project Ideas', desc: 'Synthesize actionable beginner, intermediate, and advanced practical template project templates.' },
  ];

  return (
    <div className="min-h-screen bg-bg text-primaryText relative overflow-hidden flex flex-col justify-between">
      {/* Background gradients */}
      <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] bg-primaryAccent/10 rounded-full blur-[120px]" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[600px] h-[600px] bg-secondaryAccent/10 rounded-full blur-[120px]" />

      {/* Header */}
      <header className="container mx-auto px-6 py-6 flex justify-between items-center z-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-primaryAccent to-secondaryAccent flex items-center justify-center shadow-lg shadow-primaryAccent/20">
            <BookOpen className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-secondaryText">
            Research Navigator AI
          </span>
        </div>
        <button 
          onClick={() => navigate('/workspace')}
          className="px-5 py-2.5 rounded-xl bg-white/5 border border-borderColor hover:bg-white/10 transition text-sm font-medium"
        >
          Enter Workspace
        </button>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-6 py-12 flex-grow flex flex-col items-center justify-center text-center z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="max-w-3xl"
        >
          <span className="px-4 py-1.5 rounded-full bg-primaryAccent/10 border border-primaryAccent/20 text-xs font-semibold uppercase tracking-wider text-primaryAccent inline-block mb-6">
            Google ADK 2.2.0 Powered AI Research Mentor
          </span>
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-r from-white via-primaryText to-secondaryText">
            From Research Papers to <span className="bg-clip-text text-transparent bg-gradient-to-r from-primaryAccent to-secondaryAccent">Real Implementations</span>
          </h1>
          <p className="text-lg md:text-xl text-secondaryText mb-10 leading-relaxed max-w-2xl mx-auto">
            Bridge the gap between theoretical machine learning papers and practical engineering. Upload papers, explore concepts, discover datasets, and build customized learning roadmaps.
          </p>

          {/* Quick Actions */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
            <button
              onClick={() => navigate('/workspace')}
              className="w-full sm:w-auto px-8 py-4 rounded-2xl bg-gradient-to-r from-primaryAccent to-secondaryAccent text-white font-medium hover:opacity-90 transition flex items-center justify-center gap-2 group shadow-xl shadow-primaryAccent/25"
            >
              Start Mentorship Session
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition" />
            </button>
          </div>
        </motion.div>

        {/* Feature Grid */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl w-full mt-8"
        >
          {features.map((feat, idx) => (
            <div
              key={idx}
              className="p-6 rounded-2xl bg-cardBg/30 border border-borderColor hover:border-primaryAccent/30 hover:bg-cardBg/50 transition duration-300 text-left group"
            >
              <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center text-primaryAccent group-hover:bg-primaryAccent/10 group-hover:text-secondaryAccent transition mb-5">
                <feat.icon className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">{feat.title}</h3>
              <p className="text-sm text-secondaryText leading-relaxed">{feat.desc}</p>
            </div>
          ))}
        </motion.div>
      </main>

      {/* Footer */}
      <footer className="border-t border-borderColor/50 py-8 z-10">
        <div className="container mx-auto px-6 flex flex-col sm:flex-row justify-between items-center text-sm text-secondaryText gap-4">
          <div>© 2026 Research Navigator AI. Built under Agents for Good.</div>
          <div className="flex gap-6">
            <a href="https://github.com" target="_blank" className="hover:text-white transition">GitHub</a>
            <a href="#" className="hover:text-white transition">Documentation</a>
            <a href="#" className="hover:text-white transition">About</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
