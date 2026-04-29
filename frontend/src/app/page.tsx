import Link from "next/link";
import { ArrowRight, CheckCircle2, Shield, Zap } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <nav className="border-b bg-white">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div className="font-bold text-2xl text-blue-600 tracking-tighter">GenAI PCE</div>
          <div className="space-x-4">
            <Link href="/auth/login" className="text-slate-600 hover:text-slate-900 font-medium">Login</Link>
            <Link href="/auth/signup" className="bg-blue-600 text-white px-5 py-2 rounded-lg font-medium hover:bg-blue-700 transition">Get Started</Link>
          </div>
        </div>
      </nav>

      <main>
        {/* Hero Section */}
        <section className="container mx-auto px-6 py-24 text-center">
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight max-w-4xl mx-auto mb-6">
            Ensure Perfect Product <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">Consistency</span>
          </h1>
          <p className="text-xl text-slate-600 mb-10 max-w-2xl mx-auto">
            Our multi-agent AI system analyzes your PRD, Design, and Code documentation to automatically detect conflicts, missing features, and cross-functional mismatches.
          </p>
          <div className="flex justify-center space-x-4">
            <Link href="/auth/signup" className="bg-blue-600 text-white px-8 py-4 rounded-xl font-bold text-lg hover:bg-blue-700 transition shadow-lg shadow-blue-200 flex items-center">
              Start Analyzing Now <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
            <Link href="#features" className="bg-white text-slate-700 px-8 py-4 rounded-xl font-bold text-lg hover:bg-slate-50 transition border">
              Learn More
            </Link>
          </div>
        </section>

        {/* Feature Highlights */}
        <section id="features" className="bg-white py-24">
          <div className="container mx-auto px-6">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold mb-4">Powered by Multi-Agent AI</h2>
              <p className="text-slate-600">Three specialized agents working together to bridge the gap between product, design, and engineering.</p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-12">
              <div className="p-8 rounded-2xl bg-slate-50 border border-slate-100 shadow-sm hover:shadow-md transition">
                <div className="bg-blue-100 w-12 h-12 rounded-lg flex items-center justify-center mb-6 text-blue-600">
                  <CheckCircle2 className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-bold mb-3">Product Requirements</h3>
                <p className="text-slate-600">Automatically extracts features and flows to ensure every requirement is accounted for downstream.</p>
              </div>
              <div className="p-8 rounded-2xl bg-slate-50 border border-slate-100 shadow-sm hover:shadow-md transition">
                <div className="bg-purple-100 w-12 h-12 rounded-lg flex items-center justify-center mb-6 text-purple-600">
                  <Zap className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-bold mb-3">Design & UI Logic</h3>
                <p className="text-slate-600">Analyzes design specs to find UX mismatches and unhandled edge cases compared to the PRD.</p>
              </div>
              <div className="p-8 rounded-2xl bg-slate-50 border border-slate-100 shadow-sm hover:shadow-md transition">
                <div className="bg-green-100 w-12 h-12 rounded-lg flex items-center justify-center mb-6 text-green-600">
                  <Shield className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-bold mb-3">Code Architecture</h3>
                <p className="text-slate-600">Validates implemented features and deviations directly against the product and design intentions.</p>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
