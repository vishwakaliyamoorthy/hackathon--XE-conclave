"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Briefcase, Code, PenTool, CheckCircle2 } from "lucide-react";

export default function RoleSelectionPage() {
  const [selectedRole, setSelectedRole] = useState<string | null>(null);
  const router = useRouter();

  const handleContinue = () => {
    if (selectedRole) {
      router.push("/dashboard");
    }
  };

  const roles = [
    { id: "product", title: "Product Manager", icon: <Briefcase className="h-6 w-6" />, desc: "Upload PRDs and track feature implementation." },
    { id: "design", title: "Designer", icon: <PenTool className="h-6 w-6" />, desc: "Upload UI designs and detect mismatches." },
    { id: "developer", title: "Developer", icon: <Code className="h-6 w-6" />, desc: "Upload code repos and fix inconsistencies." },
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-2xl text-center">
        <h2 className="text-3xl font-extrabold text-gray-900 mb-2">Select Your Role</h2>
        <p className="text-slate-600 mb-8">Choose how you'll interact with the Consistency Engine</p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {roles.map((role) => (
            <div
              key={role.id}
              onClick={() => setSelectedRole(role.id)}
              className={`cursor-pointer bg-white p-6 rounded-2xl border-2 transition-all duration-200 shadow-sm relative flex flex-col items-center text-center ${
                selectedRole === role.id ? "border-blue-600 ring-4 ring-blue-50" : "border-slate-100 hover:border-blue-300"
              }`}
            >
              {selectedRole === role.id && (
                <div className="absolute top-4 right-4 text-blue-600">
                  <CheckCircle2 className="h-5 w-5" />
                </div>
              )}
              <div className={`w-12 h-12 rounded-full flex items-center justify-center mb-4 ${
                selectedRole === role.id ? "bg-blue-100 text-blue-600" : "bg-slate-100 text-slate-600"
              }`}>
                {role.icon}
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">{role.title}</h3>
              <p className="text-sm text-slate-500">{role.desc}</p>
            </div>
          ))}
        </div>

        <button
          onClick={handleContinue}
          disabled={!selectedRole}
          className={`w-full sm:w-auto px-10 py-3 rounded-xl font-bold text-white transition shadow-sm ${
            selectedRole ? "bg-blue-600 hover:bg-blue-700 shadow-blue-200" : "bg-slate-300 cursor-not-allowed"
          }`}
        >
          Complete Setup
        </button>
      </div>
    </div>
  );
}
