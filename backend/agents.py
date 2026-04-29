import json
import logging
import asyncio
import os
from typing import Dict, Any, List, Optional
import openai
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# Initialize client. Assumes OPENAI_API_KEY is available in environment variables
# In a real app, you would pass this from config.py
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", "mock-key"))

def retry_on_api_error(fallback: Any = None, max_retries: int = 3, delay: float = 2.0):
    """Decorator to retry OpenAI API calls on failure, returning fallback if provided."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (openai.APIError, openai.RateLimitError, openai.APIConnectionError) as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed after {max_retries} attempts: {e}")
                        if fallback is not None:
                            logger.info("Returning fallback simulated output.")
                            return fallback
                        raise
                    logger.warning(f"API error: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                except json.JSONDecodeError as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed to parse JSON after {max_retries} attempts: {e}")
                        if fallback is not None:
                            logger.info("Returning fallback simulated output.")
                            return fallback
                        raise
                    logger.warning(f"JSON decode error: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                except Exception as e:
                    logger.error(f"Unexpected error: {e}")
                    if fallback is not None:
                        logger.info("Returning fallback simulated output.")
                        return fallback
                    raise
        return wrapper
    return decorator


class AgentSystem:
    """Multi-agent AI system for consistency analysis."""

    @staticmethod
    @retry_on_api_error(fallback={"summary": "Mock PRD Summary", "issues": ["Mock PRD issue"], "missing_features": ["Mock PRD feature"]})
    async def prd_agent(prd_text: str) -> Dict[str, Any]:
        """
        Analyzes PRD text to extract summaries, issues, and missing features.
        """
        prd_text = prd_text[:3000] # Safe limit to prevent token overflow
        logger.info("Starting PRD Agent analysis")
        prompt = f"""
You are an expert Product Manager AI. Analyze the following Product Requirements Document (PRD).
Provide your output strictly as a JSON object matching this schema:
{{
  "summary": "String summarizing the PRD",
  "issues": ["List of potential logical or clarity issues"],
  "missing_features": ["List of missing or vaguely defined features"]
}}

Do NOT include any markdown, explanation, or extra text. Only return the JSON object.

PRD Text:
{prd_text}
"""
        response = await client.chat.completions.create(
            model="gpt-4-turbo-preview",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You output strict JSON exactly as requested."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        result = json.loads(response.choices[0].message.content)
        logger.info(f"PRD RESULT: {json.dumps(result)}")
        return result

    @staticmethod
    @retry_on_api_error(fallback={"features": ["Mock code feature"], "deviations": ["Mock code deviation"]})
    async def dev_agent(code_summary: str) -> Dict[str, Any]:
        """
        Analyzes Code Summary to extract features and deviations.
        """
        code_summary = code_summary[:3000] # Safe limit to prevent token overflow
        logger.info("Starting Dev Agent analysis")
        prompt = f"""
You are an expert Tech Lead AI. Analyze the following Code Architecture/Summary.
Provide your output strictly as a JSON object matching this schema:
{{
  "features": ["List of implemented features detected"],
  "deviations": ["List of technical deviations or anti-patterns"]
}}

Do NOT include any markdown, explanation, or extra text. Only return the JSON object.

Code Summary:
{code_summary}
"""
        response = await client.chat.completions.create(
            model="gpt-4-turbo-preview",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You output strict JSON exactly as requested."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        result = json.loads(response.choices[0].message.content)
        logger.info(f"DEV RESULT: {json.dumps(result)}")
        return result

    @staticmethod
    @retry_on_api_error(fallback={"ui_elements": ["Mock UI element"], "mismatches": ["Mock UI mismatch"]})
    async def design_agent(design_description: str) -> Dict[str, Any]:
        """
        Analyzes Design Description to extract UI elements and mismatches.
        """
        design_description = design_description[:3000] # Safe limit to prevent token overflow
        logger.info("Starting Design Agent analysis")
        prompt = f"""
You are an expert UX/UI Designer AI. Analyze the following Design Description.
Provide your output strictly as a JSON object matching this schema:
{{
  "ui_elements": ["List of core UI elements described"],
  "mismatches": ["List of UX mismatches or missing flows"]
}}

Do NOT include any markdown, explanation, or extra text. Only return the JSON object.

Design Description:
{design_description}
"""
        response = await client.chat.completions.create(
            model="gpt-4-turbo-preview",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You output strict JSON exactly as requested."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        result = json.loads(response.choices[0].message.content)
        logger.info(f"DESIGN RESULT: {json.dumps(result)}")
        return result

    @staticmethod
    @retry_on_api_error(fallback={"conflicts": ["Mock conflict detected"], "suggestions": ["Mock resolution suggestion"], "actions": ["Mock actionable step"]})
    async def master_agent(prd_output: Dict, dev_output: Dict, design_output: Dict) -> Dict[str, Any]:
        """
        Analyzes outputs from all agents to find conflicts and propose actionable steps.
        """
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

Do NOT include any markdown, explanation, or extra text. Only return the JSON object.

PRD Agent Output:
{json.dumps(prd_output, indent=2)}

Dev Agent Output:
{json.dumps(dev_output, indent=2)}

Design Agent Output:
{json.dumps(design_output, indent=2)}
"""
        response = await client.chat.completions.create(
            model="gpt-4-turbo-preview",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You output strict JSON exactly as requested."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        result = json.loads(response.choices[0].message.content)
        logger.info(f"MASTER RESULT: {json.dumps(result)}")
        return result

    @staticmethod
    @retry_on_api_error(fallback="Mock updated PRD content based on suggestions.")
    async def prd_update_agent(original_text: str, suggestions: List[str]) -> str:
        """Updates PRD text based on AI suggestions."""
        logger.info("Starting PRD Update Agent")
        prompt = f"""
You are an expert Product Manager AI. Rewrite the following PRD to incorporate the resolution suggestions.
Return ONLY the raw updated text. Do not return JSON.

Original PRD:
{original_text[:3000]}

Suggestions to Apply:
{json.dumps(suggestions, indent=2)}
"""
        response = await client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that directly outputs updated document text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content

    @staticmethod
    @retry_on_api_error(fallback="Mock updated Code summary based on suggestions.")
    async def dev_update_agent(original_text: str, suggestions: List[str]) -> str:
        """Updates Code Summary based on AI suggestions."""
        logger.info("Starting Dev Update Agent")
        prompt = f"""
You are an expert Tech Lead AI. Rewrite the following Code Summary to incorporate the resolution suggestions.
Return ONLY the raw updated text. Do not return JSON.

Original Code Summary:
{original_text[:3000]}

Suggestions to Apply:
{json.dumps(suggestions, indent=2)}
"""
        response = await client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that directly outputs updated document text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content

    @staticmethod
    @retry_on_api_error(fallback="Mock updated Design description based on suggestions.")
    async def design_update_agent(original_text: str, suggestions: List[str]) -> str:
        """Updates Design Description based on AI suggestions."""
        logger.info("Starting Design Update Agent")
        prompt = f"""
You are an expert UX/UI Designer AI. Rewrite the following Design Description to incorporate the resolution suggestions.
Return ONLY the raw updated text. Do not return JSON.

Original Design Description:
{original_text[:3000]}

Suggestions to Apply:
{json.dumps(suggestions, indent=2)}
"""
        response = await client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that directly outputs updated document text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content

async def run_analysis_pipeline(prd_text: str, code_summary: str, design_desc: str) -> Dict[str, Any]:
    """
    Runs the complete multi-agent pipeline concurrently, then runs the master agent.
    """
    logger.info("Starting multi-agent pipeline")
    
    # Run specialized agents concurrently
    prd_task = asyncio.create_task(AgentSystem.prd_agent(prd_text))
    dev_task = asyncio.create_task(AgentSystem.dev_agent(code_summary))
    design_task = asyncio.create_task(AgentSystem.design_agent(design_desc))
    
    prd_res, dev_res, design_res = await asyncio.gather(prd_task, dev_task, design_task)
    
    # Run Master Orchestrator
    master_res = await AgentSystem.master_agent(prd_res, dev_res, design_res)
    
    return {
        "prd_analysis": prd_res,
        "dev_analysis": dev_res,
        "design_analysis": design_res,
        "master_analysis": master_res
    }
