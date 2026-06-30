/**
 * Helper utility to parse the generated Markdown Mentorship Report
 * into structured components for the Dashboard, Roadmap, and Report views.
 */
export function parseReport(markdownText) {
  if (!markdownText) return null;

  const sections = {
    raw: markdownText,
    summary: "",
    prerequisites: "",
    datasets: "",
    complexity: "",
    readinessScore: 0,
    readinessExplanation: "",
    learningPlan: [],
    feasibility: { level: "Medium", justification: "" },
    projects: [],
    impact: "",
    recommendations: ""
  };

  // Helper to extract content between two headings
  const extractSection = (headings, nextHeadings) => {
    const lines = markdownText.split("\n");
    let capturing = false;
    const capturedLines = [];

    for (let line of lines) {
      const isHeading = line.startsWith("#");
      const cleanLine = line.replace(/^[#\s*-_]+|[#\s*-_]+$/g, "").toLowerCase();

      if (isHeading) {
        const matchesHeading = headings.some(h => cleanLine.includes(h.toLowerCase()));
        const matchesNext = nextHeadings.some(nh => cleanLine.includes(nh.toLowerCase()));

        if (matchesHeading) {
          capturing = true;
          continue;
        } else if (matchesNext && capturing) {
          capturing = false;
          break;
        }
      }

      if (capturing) {
        capturedLines.push(line);
      }
    }
    return capturedLines.join("\n").trim();
  };

  // 1. Executive Summary
  sections.summary = extractSection(
    ["executive summary", "summary", "introduction"],
    ["prerequisite analysis", "prerequisites", "dataset details"]
  );

  // 2. Prerequisites
  sections.prerequisites = extractSection(
    ["prerequisite analysis", "prerequisites"],
    ["dataset details", "datasets", "complexity assessment"]
  );

  // 3. Datasets
  sections.datasets = extractSection(
    ["dataset details", "datasets", "dataset suggestions"],
    ["complexity assessment", "complexity", "research readiness score"]
  );

  // 4. Complexity
  sections.complexity = extractSection(
    ["complexity assessment", "complexity", "hardware requirements"],
    ["research readiness score", "readiness score", "readiness analysis"]
  );

  // 5. Readiness Score & Explanation
  const readinessText = extractSection(
    ["research readiness score", "readiness score", "readiness analysis"],
    ["weekly learning plan", "learning plan", "learning roadmap"]
  );
  sections.readinessExplanation = readinessText;

  // Extract readiness score number (e.g. 45/100 or 45 out of 100)
  const scoreMatch = readinessText.match(/(\d+)\s*\/\s*100/) || readinessText.match(/(\d+)\s*out of\s*100/);
  if (scoreMatch) {
    sections.readinessScore = parseInt(scoreMatch[1], 10);
  } else {
    const fallbackMatch = readinessText.match(/\b(\d{2})\b/);
    if (fallbackMatch) {
      sections.readinessScore = parseInt(fallbackMatch[1], 10);
    }
  }

  // 6. Weekly Learning Plan
  const learningText = extractSection(
    ["weekly learning plan", "learning plan", "learning roadmap"],
    ["research feasibility", "feasibility"]
  );

  // Parse weeks (Week 1 to Week 4)
  const weekBlocks = learningText.split(/(?=Week \d+:|### Week \d+:|#### Week \d+:)/i);
  const parsedWeeks = [];
  weekBlocks.forEach(block => {
    if (!block.trim()) return;
    const weekTitleMatch = block.match(/(Week \d+):?\s*(.*)/i);
    if (weekTitleMatch) {
      const title = weekTitleMatch[1];
      const rest = block.replace(weekTitleMatch[0], "").trim();
      parsedWeeks.push({
        week: title,
        content: rest
      });
    }
  });
  sections.learningPlan = parsedWeeks;

  // 7. Research Feasibility
  const feasibilityText = extractSection(
    ["research feasibility", "feasibility"],
    ["suggested projects", "projects", "research impact"]
  );
  sections.feasibility.justification = feasibilityText;
  
  if (feasibilityText.toLowerCase().includes("high")) {
    sections.feasibility.level = "High";
  } else if (feasibilityText.toLowerCase().includes("low")) {
    sections.feasibility.level = "Low";
  } else {
    sections.feasibility.level = "Medium";
  }

  // 8. Suggested Projects
  const projectsText = extractSection(
    ["suggested projects", "projects"],
    ["research impact", "impact", "mentor suitability"]
  );
  
  const projectBlocks = projectsText.split(/(?=\*\s*\*\*Beginner|\*\s*\*\*Intermediate|\*\s*\*\*Advanced|### Beginner|### Intermediate|### Advanced)/i);
  const parsedProjects = [];
  projectBlocks.forEach(block => {
    if (!block.trim()) return;
    const titleMatch = block.match(/(\*\*Beginner.*?\*\*|\*\*Intermediate.*?\*\*|\*\*Advanced.*?\*\*|Beginner|Intermediate|Advanced)/i);
    if (titleMatch) {
      parsedProjects.push({
        title: titleMatch[1].replace(/\*\*/g, ""),
        content: block.replace(titleMatch[0], "").trim()
      });
    }
  });
  sections.projects = parsedProjects;

  // 9. Research Impact
  sections.impact = extractSection(
    ["research impact", "impact"],
    ["mentor suitability", "recommendations"]
  );

  // 10. Recommendations & Suitability
  sections.recommendations = extractSection(
    ["mentor suitability", "recommendations"],
    [""] // Capture until end
  );

  return sections;
}
