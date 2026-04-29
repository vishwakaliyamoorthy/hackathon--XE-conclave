import os
import logging
from typing import Dict, Any, List, Optional
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class DatabaseService:
    """
    Supabase CRUD Service managing projects, documents, and AI analysis results.
    Connects to the specific tables: users, projects, prds, designs, code_summaries, analysis_results.
    """
    
    def __init__(self):
        """Initialize connection using secure environment variables."""
        # Using environment variables ensures secure usage without hardcoding credentials
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            logger.warning("SUPABASE_URL or SUPABASE_KEY is missing. Database operations will fail.")
            
        self.client: Client = create_client(self.supabase_url or "", self.supabase_key or "")

    # ==== CRUD Operations ====

    def insert_prd(self, project_id: str, title: str, content: str) -> Dict[str, Any]:
        """Insert a Product Requirements Document (PRD)."""
        logger.info(f"Inserting PRD for project: {project_id}")
        data = {
            "project_id": project_id,
            "title": title,
            "content": content
        }
        response = self.client.table("prds").insert(data).execute()
        return response.data[0] if response.data else {}

    def insert_design(self, project_id: str, title: str, content: str) -> Dict[str, Any]:
        """Insert a Design Document."""
        logger.info(f"Inserting Design for project: {project_id}")
        data = {
            "project_id": project_id,
            "title": title,
            "content": content
        }
        response = self.client.table("designs").insert(data).execute()
        return response.data[0] if response.data else {}

    def insert_code(self, project_id: str, repo_url: str, content: str) -> Dict[str, Any]:
        """Insert a Code Summary Document."""
        logger.info(f"Inserting Code Summary for project: {project_id}")
        data = {
            "project_id": project_id,
            "repo_url": repo_url,
            "content": content
        }
        response = self.client.table("code_summaries").insert(data).execute()
        return response.data[0] if response.data else {}

    def fetch_project_data(self, project_id: str) -> Dict[str, Any]:
        """Fetch all related project data including PRDs, designs, code summaries, and analysis."""
        logger.info(f"Fetching full project data for: {project_id}")
        
        project = self.client.table("projects").select("*").eq("id", project_id).execute()
        prds = self.client.table("prds").select("*").eq("project_id", project_id).execute()
        designs = self.client.table("designs").select("*").eq("project_id", project_id).execute()
        code_summaries = self.client.table("code_summaries").select("*").eq("project_id", project_id).execute()
        analysis_results = self.client.table("analysis_results").select("*").eq("project_id", project_id).execute()

        return {
            "project": project.data[0] if project.data else None,
            "prds": prds.data,
            "designs": designs.data,
            "code_summaries": code_summaries.data,
            "analysis_results": analysis_results.data
        }

    def store_analysis_results(self, project_id: str, agent_outputs: Dict[str, Any], master_output: Dict[str, Any]) -> Dict[str, Any]:
        """Store the AI consistency analysis results from the agents."""
        logger.info(f"Storing analysis results for project: {project_id}")
        
        data = {
            "project_id": project_id,
            "agent_outputs": agent_outputs,
            "master_output": master_output,
            "conflicts_count": len(master_output.get("conflicts", [])),
            "status": "completed"
        }
        response = self.client.table("analysis_results").insert(data).execute()
        return response.data[0] if response.data else {}

# Initialize a global singleton instance for FastAPI injection
db = DatabaseService()
