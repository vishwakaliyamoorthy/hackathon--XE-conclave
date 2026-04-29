import json
import logging
import asyncio
import os
from typing import Dict, Any, List, Optional
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.warning("GEMINI_API_KEY not found in environment variables")
genai.configure(api_key=api_key)

MODEL_NAME = "gemini-1.5-flash"

def retry_on_api_error(fallback: Any = None, max_retries: int = 3, delay: float = 2.0):
    """Decorator to retry API calls on failure."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed after {max_retries} attempts: {e}")
                        if fallback is not None:
                            logger.info("Returning fallback simulated output.")
                            return fallback
                        raise
                    logger.warning(f"API error: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator


class AgentSystem:
    """Multi-agent AI system for consistency analysis using Gemini."""

    @staticmethod
    @retry_on_api_error(fallback={"summary": "Fallback summary", "issues": ["Fallback issue"], "missing_features": ["Fallback missing"]})
    async def prd_agent(prd_text: str) -> Dict[str, Any]:
        prd_text = prd_text[:10000] 
        logger.info("Starting PRD Agent analysis")
        prompt = f"""
You are an expert Product Manager AI. Analyze the following Product Requirements Document (PRD).
Provide your output strictly as a JSON object matching this schema:
{{
  "summary": "String summarizing the PRD",
  "issues": ["List of potential logical or clarity issues"],
  "missing_features": ["List of missing or vaguely defined features"]
}}

PRD Text:
{prd_text}
"""
        model = genai.GenerativeModel(MODEL_NAME)
        response = await model.generate_content_async(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        result = json.loads(response.text)
        logger.info(f"PRD RESULT: {json.dumps(result)}")
        return result

    @staticmethod
    @retry_on_api_error(fallback={"features": ["Fallback feature"], "deviations": ["Fallback deviation"]})
    async def dev_agent(code_summary: str) -> Dict[str, Any]:
        code_summary = code_summary[:10000]
        logger.info("Starting Dev Agent analysis")
        prompt = f"""
You are an expert Tech Lead AI. Analyze the following Code Architecture/Summary.
Provide your output strictly as a JSON object matching this schema:
{{
  "features": ["List of implemented features detected"],
  "deviations": ["List of technical deviations or anti-patterns"]
}}

Code Summary:
{code_summary}
"""
        model = genai.GenerativeModel(MODEL_NAME)
        response = await model.generate_content_async(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        result = json.loads(response.text)
        logger.info(f"DEV RESULT: {json.dumps(result)}")
        return result

    @staticmethod
    @retry_on_api_error(fallback={"ui_elements": ["Fallback element"], "mismatches": ["Fallback mismatch"]})
    async def design_agent(design_description: str) -> Dict[str, Any]:
        design_description = design_description[:10000]
        logger.info("Starting Design Agent analysis")
        prompt = f"""
You are an expert UX/UI Designer AI. Analyze the following Design Description.
Provide your output strictly as a JSON object matching this schema:
{{
  "ui_elements": ["List of core UI elements described"],
  "mismatches": ["List of UX mismatches or missing flows"]
}}

Design Description:
{design_description}
"""
        model = genai.GenerativeModel(MODEL_NAME)
        response = await model.generate_content_async(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        result = json.loads(response.text)
        logger.info(f"DESIGN RESULT: {json.dumps(result)}")
        return result

    @staticmethod
    @retry_on_api_error(fallback={"conflicts": ["Fallback conflict"], "suggestions": ["Fallback suggestion"], "actions": ["Fallback action"]})
    async def master_agent(prd_output: Dict, dev_output: Dict, design_output: Dict) -> Dict[str, Any]:
        logger.info("Starting Master Agent analysis")
        prompt = f"""
You are a Master Orchestrator AI. Compare the findings of the PRD, Dev, and Design agents.
Find cross-functional conflicts, make suggestions, and propose actionable steps.

Provide your output strictly as a JSON object matching this schema:
{{
  "conflicts": ["List of cross-functional conflicts (e.g., feature in PRD but missing in Dev)"],
  "suggestions": ["List of strategic suggestions to resolve conflicts"],
  "actions": ["List of concrete next steps for the team"]
}}

PRD Agent Output:
{json.dumps(prd_output, indent=2)}

Dev Agent Output:
{json.dumps(dev_output, indent=2)}

Design Agent Output:
{json.dumps(design_output, indent=2)}
"""
        model = genai.GenerativeModel(MODEL_NAME)
        response = await model.generate_content_async(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        result = json.loads(response.text)
        logger.info(f"MASTER RESULT: {json.dumps(result)}")
        return result

    @staticmethod
    @retry_on_api_error(fallback="Mock updated PRD content")
    async def prd_update_agent(original_text: str, suggestions: List[str]) -> str:
        logger.info("Starting PRD Update Agent")
        prompt = f"""
You are an expert Product Manager AI. Rewrite the following PRD to incorporate the resolution suggestions.
Return ONLY the raw updated text. Do not return JSON.

Original PRD:
{original_text[:10000]}

Suggestions to Apply:
{json.dumps(suggestions, indent=2)}
"""
        model = genai.GenerativeModel(MODEL_NAME)
        response = await model.generate_content_async(prompt)
        return response.text

    @staticmethod
    @retry_on_api_error(fallback="Mock updated Code summary")
    async def dev_update_agent(original_text: str, suggestions: List[str]) -> str:
        logger.info("Starting Dev Update Agent")
        prompt = f"""
You are an expert Tech Lead AI. Rewrite the following Code Summary to incorporate the resolution suggestions.
Return ONLY the raw updated text. Do not return JSON.

Original Code Summary:
{original_text[:10000]}

Suggestions to Apply:
{json.dumps(suggestions, indent=2)}
"""
        model = genai.GenerativeModel(MODEL_NAME)
        response = await model.generate_content_async(prompt)
        return response.text

    @staticmethod
    @retry_on_api_error(fallback="Mock updated Design description")
    async def design_update_agent(original_text: str, suggestions: List[str]) -> str:
        logger.info("Starting Design Update Agent")
        prompt = f"""
You are an expert UX/UI Designer AI. Rewrite the following Design Description to incorporate the resolution suggestions.
Return ONLY the raw updated text. Do not return JSON.

Original Design Description:
{original_text[:10000]}

Suggestions to Apply:
{json.dumps(suggestions, indent=2)}
"""
        model = genai.GenerativeModel(MODEL_NAME)
        response = await model.generate_content_async(prompt)
        return response.text

async def run_analysis_pipeline(prd_text: str, code_summary: str, design_desc: str) -> Dict[str, Any]:
    logger.info("Starting multi-agent pipeline")
    
    prd_task = asyncio.create_task(AgentSystem.prd_agent(prd_text))
    dev_task = asyncio.create_task(AgentSystem.dev_agent(code_summary))
    design_task = asyncio.create_task(AgentSystem.design_agent(design_desc))
    
    prd_res, dev_res, design_res = await asyncio.gather(prd_task, dev_task, design_task)
    
    master_res = await AgentSystem.master_agent(prd_res, dev_res, design_res)
    
    return {
        "prd_analysis": prd_res,
        "dev_analysis": dev_res,
        "design_analysis": design_res,
        "master_analysis": master_res
    }
