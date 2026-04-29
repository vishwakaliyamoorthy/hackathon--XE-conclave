"use client";

import { useState } from "react";
import Link from "next/link";
import { UploadCloud, FileText, Image as ImageIcon, Code, ArrowRight, Play } from "lucide-react";
import { useRouter } from "next/navigation";

export default function DashboardPage() {
  const router = useRouter();
  
  // Real file states
  const [prdFile, setPrdFile] = useState<File | null>(null);
  const [designFile, setDesignFile] = useState<File | null>(null);
  const [codeFile, setCodeFile] = useState<File | null>(null);
  
  const [analyzing, setAnalyzing] = useState(false);

  // Reusable upload function
  const uploadFile = async (file: File, type: string) => {
    const token = localStorage.getItem("token") || "dummy_token";
    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", file.name); // Using file name as title
    
    const response = await fetch(`http://localhost:8000/api/upload/${type}`, {
      method: "POST",
      headers: { "Authorization": `Bearer ${token}` }, // Do NOT set Content-Type for FormData
      body: formData
    });
    
    if (response.status === 401) {
      localStorage.removeItem("token");
      router.push("/auth/login");
      throw new Error("Session expired. Please log in again.");
    }
    
    if (!response.ok) {
      throw new Error(`Failed to upload ${type} document`);
    }
    
    return await response.json();
  };

  const handleUploadAndAnalyze = async () => {
    if (!prdFile && !designFile && !codeFile) {
      alert("Please upload at least one file to analyze.");
      return;
    }

    setAnalyzing(true);
    try {
      const token = localStorage.getItem("token") || "dummy_token";
      let prdId = null;
      let designId = null;
      let codeId = null;

      // 1. Upload Files
      if (prdFile) {
        const res = await uploadFile(prdFile, "prd");
        prdId = res.id;
        console.log(`Uploaded PRD, ID: ${prdId}`);
      }
      if (designFile) {
        const res = await uploadFile(designFile, "design");
        designId = res.id;
        console.log(`Uploaded Design, ID: ${designId}`);
      }
      if (codeFile) {
        const res = await uploadFile(codeFile, "code");
        codeId = res.id;
        console.log(`Uploaded Code, ID: ${codeId}`);
      }
      
      // 2. Create Analysis Session
      const createRes = await fetch("http://localhost:8000/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
        body: JSON.stringify({ title: "New Project Analysis", description: "Uploaded from Dashboard" })
      });
      
      if (!createRes.ok) throw new Error("Failed to create analysis");
      const analysisData = await createRes.json();
      const analysisId = analysisData.id;
      
      // 3. Link Documents
      await fetch(`http://localhost:8000/api/analyze/${analysisId}/link-documents`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
        body: JSON.stringify({
          prd_doc_id: prdId,
          design_doc_id: designId,
          code_doc_id: codeId
        })
      });
      
      // 4. Start Analysis
      await fetch(`http://localhost:8000/api/analyze/${analysisId}/start`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` }
      });
      
      // Navigate to analysis page with ID
      router.push(`/analysis?id=${analysisId}`);
    } catch (error: any) {
      console.error("Analysis Error:", error);
      alert(error.message || "Failed to start analysis. Check console.");
      setAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="border-b bg-white sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <Link href="/" className="font-bold text-xl text-blue-600 tracking-tighter">GenAI PCE</Link>
          <div className="flex items-center space-x-4">
            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-sm">
              JD
            </div>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-6 py-12 max-w-5xl">
        <div className="mb-10">
          <h1 className="text-3xl font-extrabold text-slate-900 mb-2">New Analysis Project</h1>
          <p className="text-slate-600">Upload your product documentation, designs, and codebase to detect inconsistencies.</p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-10">
          {/* PRD Upload */}
          <div className={`bg-white p-6 rounded-2xl border-2 transition ${prdFile ? 'border-green-500' : 'border-slate-200 border-dashed'}`}>
            <div className="flex justify-between items-start mb-4">
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${prdFile ? 'bg-green-100 text-green-600' : 'bg-slate-100 text-slate-500'}`}>
                <FileText className="h-6 w-6" />
              </div>
              {prdFile && <span className="bg-green-100 text-green-700 text-xs font-bold px-2 py-1 rounded">Uploaded</span>}
            </div>
            <h3 className="font-bold text-lg mb-1">Product Requirements</h3>
            <p className="text-slate-500 text-sm mb-4">PDF, Markdown, or Notion export</p>
            <div className="relative">
              <input 
                type="file" 
                id="prd-upload"
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                onChange={(e) => setPrdFile(e.target.files?.[0] || null)}
              />
              <div className={`w-full py-2 rounded-lg font-medium text-sm flex items-center justify-center transition pointer-events-none ${prdFile ? 'bg-slate-100 text-slate-700' : 'bg-blue-50 text-blue-600'}`}>
                {prdFile ? prdFile.name : <><UploadCloud className="h-4 w-4 mr-2"/> Browse Files</>}
              </div>
            </div>
          </div>

          {/* Design Upload */}
          <div className={`bg-white p-6 rounded-2xl border-2 transition ${designFile ? 'border-green-500' : 'border-slate-200 border-dashed'}`}>
            <div className="flex justify-between items-start mb-4">
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${designFile ? 'bg-green-100 text-green-600' : 'bg-slate-100 text-slate-500'}`}>
                <ImageIcon className="h-6 w-6" />
              </div>
              {designFile && <span className="bg-green-100 text-green-700 text-xs font-bold px-2 py-1 rounded">Uploaded</span>}
            </div>
            <h3 className="font-bold text-lg mb-1">Design Assets</h3>
            <p className="text-slate-500 text-sm mb-4">Figma link, Images, or ZIP</p>
            <div className="relative">
              <input 
                type="file" 
                id="design-upload"
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                onChange={(e) => setDesignFile(e.target.files?.[0] || null)}
              />
              <div className={`w-full py-2 rounded-lg font-medium text-sm flex items-center justify-center transition pointer-events-none ${designFile ? 'bg-slate-100 text-slate-700' : 'bg-blue-50 text-blue-600'}`}>
                {designFile ? designFile.name : <><UploadCloud className="h-4 w-4 mr-2"/> Browse Files</>}
              </div>
            </div>
          </div>

          {/* Code Upload */}
          <div className={`bg-white p-6 rounded-2xl border-2 transition ${codeFile ? 'border-green-500' : 'border-slate-200 border-dashed'}`}>
            <div className="flex justify-between items-start mb-4">
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${codeFile ? 'bg-green-100 text-green-600' : 'bg-slate-100 text-slate-500'}`}>
                <Code className="h-6 w-6" />
              </div>
              {codeFile && <span className="bg-green-100 text-green-700 text-xs font-bold px-2 py-1 rounded">Uploaded</span>}
            </div>
            <h3 className="font-bold text-lg mb-1">Source Code</h3>
            <p className="text-slate-500 text-sm mb-4">Github repo link or ZIP</p>
            <div className="relative">
              <input 
                type="file" 
                id="code-upload"
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                onChange={(e) => setCodeFile(e.target.files?.[0] || null)}
              />
              <div className={`w-full py-2 rounded-lg font-medium text-sm flex items-center justify-center transition pointer-events-none ${codeFile ? 'bg-slate-100 text-slate-700' : 'bg-blue-50 text-blue-600'}`}>
                {codeFile ? codeFile.name : <><UploadCloud className="h-4 w-4 mr-2"/> Browse Files</>}
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <button 
            onClick={handleUploadAndAnalyze}
            disabled={!(prdFile || designFile || codeFile) || analyzing}
            className={`px-8 py-3 rounded-xl font-bold flex items-center transition shadow-sm ${
              (prdFile || designFile || codeFile) && !analyzing
                ? "bg-blue-600 text-white hover:bg-blue-700 shadow-blue-200" 
                : "bg-slate-300 text-slate-500 cursor-not-allowed"
            }`}
          >
            {analyzing ? (
              <span className="flex items-center">Uploading & Analyzing... <div className="ml-2 w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div></span>
            ) : (
              <span className="flex items-center">Upload & Analyze <Play className="ml-2 h-4 w-4 fill-current"/></span>
            )}
          </button>
        </div>

        {/* Recent Projects Placeholder */}
        <div className="mt-20">
          <h2 className="text-xl font-bold text-slate-900 mb-6">Recent Projects</h2>
          <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
            <div className="p-6 border-b border-slate-100 flex items-center justify-between hover:bg-slate-50 transition cursor-pointer">
              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 rounded-lg bg-indigo-100 text-indigo-600 flex items-center justify-center font-bold">
                  E
                </div>
                <div>
                  <h4 className="font-bold text-slate-900">E-Commerce Checkout Flow</h4>
                  <p className="text-sm text-slate-500">Analyzed 2 days ago</p>
                </div>
              </div>
              <div className="flex items-center space-x-6">
                <div className="text-sm text-slate-500 hidden md:block">
                  <span className="text-red-500 font-bold">3</span> Conflicts
                </div>
                <ArrowRight className="h-5 w-5 text-slate-400" />
              </div>
            </div>
            <div className="p-6 flex items-center justify-between hover:bg-slate-50 transition cursor-pointer">
              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 rounded-lg bg-orange-100 text-orange-600 flex items-center justify-center font-bold">
                  S
                </div>
                <div>
                  <h4 className="font-bold text-slate-900">SaaS Onboarding Dashboard</h4>
                  <p className="text-sm text-slate-500">Analyzed last week</p>
                </div>
              </div>
              <div className="flex items-center space-x-6">
                <div className="text-sm text-slate-500 hidden md:block">
                  <span className="text-green-500 font-bold">0</span> Conflicts
                </div>
                <ArrowRight className="h-5 w-5 text-slate-400" />
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
