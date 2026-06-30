import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import Workspace from './pages/Workspace';
import Dashboard from './pages/Dashboard';
import Roadmap from './pages/Roadmap';
import Report from './pages/Report';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/workspace" element={<Workspace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/roadmap" element={<Roadmap />} />
        <Route path="/report" element={<Report />} />
      </Routes>
    </Router>
  );
}
