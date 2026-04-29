"use client";

import Link from "next/link";
import { AlertCircle, CheckCircle2, ChevronDown, ChevronRight, FileText, Code, PenTool, Lightbulb } from "lucide-react";
import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";

function AnalysisContent() {
  const searchParams = useSearchParams();
  const analysisId = searchParams.get("id");
  const [expandedConflict, setExpandedConflict] = useState<number | null>(1);
  const [conflicts, setConflicts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [approving, setApproving] = useState(false);

  const handleApprove = async () => {
    if (!analysisId) return;
    setApproving(true);
    try {
      const token = localStorage.getItem("token") || "dummy_token";
      const res = await fetch(`http://localhost:8000/api/analyze/${analysisId}/approve`, {
        method: "POST",
        headers: { 
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ approved: true })
      });
      
      const data = await res.json();
      if (res.ok && data.status === "updated") {
        alert("Document updated successfully! New version created.");
      } else {
        alert(data.message || "Approval failed.");
      }
    } catch (err) {
      console.error(err);
      alert("An error occurred during approval.");
    } finally {
      setApproving(false);
    }
  };

  useEffect(() => {
    if (!analysisId) {
      setError("No analysis ID provided.");
      setLoading(false);
      return;
    }

    const fetchResults = async () => {
      try {
        const token = localStorage.getItem("token") || "dummy_token";
        const res = await fetch(`http://localhost:8000/api/analyze/${analysisId}/results`, {
          headers: { "Authorization": `Bearer ${token}` }
        });

        if (!res.ok) throw new Error("Failed to fetch results");

        const data = await res.json();
        
        if (data.status === "processing") {
          // Still processing, poll again
          setTimeout(fetchResults, 2000);
          return;
        }

        setConflicts(data.conflicts || []);
        setLoading(false);
      } catch (err: any) {
        console.error(err);
        setError("Error loading analysis results.");
        setLoading(false);
      }
    };

    fetchResults();
  }, [analysisId]);

  if (loading) return <div className="min-h-screen bg-slate-50 flex items-center justify-center font-bold text-xl text-slate-500">Loading Analysis...</div>;
  if (error) return <div className="min-h-screen bg-slate-50 flex items-center justify-center font-bold text-xl text-red-500">{error}</div>;



  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <nav className="border-b bg-white sticky top-0 z-10 shadow-sm">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <Link href="/dashboard" className="text-slate-500 hover:text-slate-900 transition font-medium text-sm">&larr; Back to Dashboard</Link>
            <div className="h-4 w-px bg-slate-300"></div>
            <span className="font-bold text-slate-900">Analysis Results</span>
          </div>
          <div className="flex space-x-3">
            <button 
              onClick={handleApprove}
              disabled={approving || conflicts.length === 0}
              className="bg-green-600 text-white px-4 py-2 rounded-lg font-medium text-sm hover:bg-green-700 transition disabled:opacity-50"
            >
              {approving ? "Updating..." : "Approve Changes"}
            </button>
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium text-sm hover:bg-blue-700 transition">
              Export Report
            </button>
          </div>
        </div>
      </nav>

      <div className="flex-1 container mx-auto px-6 py-8 flex flex-col lg:flex-row gap-8 max-w-7xl">
        {/* Left Column - Summary */}
        <div className="lg:w-1/3 space-y-6">
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
            <h2 className="text-lg font-bold mb-4">Project Overview</h2>
            <div className="flex items-center justify-between mb-6 pb-6 border-b border-slate-100">
              <div>
                <p className="text-sm text-slate-500 mb-1">Status</p>
                <div className="flex items-center text-red-600 font-bold">
                  <AlertCircle className="h-4 w-4 mr-1" />
                  Conflicts Found
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm text-slate-500 mb-1">Total Issues</p>
                <p className="text-2xl font-black text-slate-900">{conflicts.length}</p>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-sm font-bold text-slate-900">Analyzed Sources</h3>
              <div className="flex items-center text-sm text-slate-600">
                <FileText className="h-4 w-4 mr-3 text-blue-500" />
                PRD_v2.pdf <span className="ml-auto text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">Processed</span>
              </div>
              <div className="flex items-center text-sm text-slate-600">
                <PenTool className="h-4 w-4 mr-3 text-purple-500" />
                Figma URLs <span className="ml-auto text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">Processed</span>
              </div>
              <div className="flex items-center text-sm text-slate-600">
                <Code className="h-4 w-4 mr-3 text-green-500" />
                GitHub Repo <span className="ml-auto text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">Processed</span>
              </div>
            </div>
          </div>

          <div className="bg-blue-50 rounded-2xl p-6 border border-blue-100">
            <div className="flex items-start">
              <Lightbulb className="h-6 w-6 text-blue-600 mr-3 shrink-0" />
              <div>
                <h3 className="font-bold text-blue-900 mb-1">Agent Insight</h3>
                <p className="text-sm text-blue-800 leading-relaxed">
                  Overall, the codebase closely follows the design, but there are functional gaps based on the PRD. Prioritize implementing the missing Export feature to reach MVP requirements.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Conflict Details */}
        <div className="lg:w-2/3">
          <h2 className="text-2xl font-extrabold text-slate-900 mb-6">Detailed Findings</h2>
          
          <div className="space-y-4">
            {conflicts.map((conflict) => (
              <div key={conflict.id} className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
                <div 
                  className="p-5 cursor-pointer hover:bg-slate-50 transition flex items-center justify-between"
                  onClick={() => setExpandedConflict(expandedConflict === conflict.id ? null : conflict.id)}
                >
                  <div className="flex items-center space-x-4">
                    <div className={`w-2 h-2 rounded-full ${
                      conflict.severity === 'high' ? 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]' : 
                      conflict.severity === 'medium' ? 'bg-orange-500' : 'bg-yellow-500'
                    }`} />
                    <h3 className="font-bold text-lg text-slate-900">{conflict.title}</h3>
                  </div>
                  {expandedConflict === conflict.id ? (
                    <ChevronDown className="h-5 w-5 text-slate-400" />
                  ) : (
                    <ChevronRight className="h-5 w-5 text-slate-400" />
                  )}
                </div>

                {expandedConflict === conflict.id && (
                  <div className="p-5 pt-0 border-t border-slate-100 mt-2 bg-slate-50/50">
                    <div className="py-4">
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Description</h4>
                      <p className="text-slate-700 mb-6">{conflict.description}</p>

                      <div className="grid md:grid-cols-2 gap-6 mb-6">
                        <div>
                          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Sources</h4>
                          <ul className="space-y-2">
                            {conflict.sources.map((source, idx) => (
                              <li key={idx} className="text-sm text-slate-600 bg-white px-3 py-2 rounded-lg border border-slate-200 font-mono text-xs">
                                {source}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>

                      <div className="bg-green-50 p-4 rounded-xl border border-green-100 flex items-start">
                        <CheckCircle2 className="h-5 w-5 text-green-600 mr-3 mt-0.5 shrink-0" />
                        <div>
                          <h4 className="font-bold text-green-900 mb-1">Resolution Suggestion</h4>
                          <p className="text-sm text-green-800">{conflict.suggestion}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function AnalysisPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-slate-50 flex items-center justify-center font-bold text-xl text-slate-500">Loading App...</div>}>
      <AnalysisContent />
    </Suspense>
  );
}
