from openai import AsyncOpenAI
import os
from typing import Dict, List, Any
import json

class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    async def analyze_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze lead data using GPT model to determine quality and potential
        """
        prompt = self._create_lead_analysis_prompt(lead_data)
        
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": "You are an expert marketing analyst specializing in lead qualification."
            }, {
                "role": "user",
                "content": prompt
            }],
            temperature=0.3
        )
        
        return json.loads(response.choices[0].message.content)
        
    async def generate_personalized_content(
        self,
        lead_profile: Dict[str, Any],
        campaign_type: str,
        tone: str = "professional"
    ) -> Dict[str, Any]:
        """
        Generate personalized marketing content based on lead profile
        """
        prompt = self._create_content_prompt(lead_profile, campaign_type, tone)
        
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": "You are an expert marketing copywriter specializing in personalized content."
            }, {
                "role": "user",
                "content": prompt
            }],
            temperature=0.7
        )
        
        return json.loads(response.choices[0].message.content)
        
    async def optimize_campaign_strategy(
        self,
        campaign_data: Dict[str, Any],
        performance_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze campaign performance and generate optimization recommendations
        """
        prompt = self._create_optimization_prompt(campaign_data, performance_metrics)
        
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": "You are an expert marketing strategist specializing in campaign optimization."
            }, {
                "role": "user",
                "content": prompt
            }],
            temperature=0.4
        )
        
        return json.loads(response.choices[0].message.content)
        
    def _create_lead_analysis_prompt(self, lead_data: Dict[str, Any]) -> str:
        return f"""
        Analyze the following lead data and provide:
        1. Lead quality score (0-100)
        2. Recommended engagement strategy
        3. Key insights about the lead
        4. Risk factors
        5. Opportunity assessment

        Lead Data:
        {json.dumps(lead_data, indent=2)}

        Provide the response in JSON format with the following structure:
        {{
            "quality_score": number,
            "engagement_strategy": string,
            "insights": [string],
            "risk_factors": [string],
            "opportunity_assessment": {{
                "potential_value": string,
                "recommended_actions": [string],
                "timeline": string
            }}
        }}
        """
        
    def _create_content_prompt(
        self,
        lead_profile: Dict[str, Any],
        campaign_type: str,
        tone: str
    ) -> str:
        return f"""
        Generate personalized marketing content based on:
        
        Lead Profile:
        {json.dumps(lead_profile, indent=2)}
        
        Campaign Type: {campaign_type}
        Tone: {tone}

        Provide the response in JSON format with the following structure:
        {{
            "subject_line": string,
            "main_content": string,
            "call_to_action": string,
            "personalization_elements": [string],
            "a_b_variants": [
                {{
                    "variant": string,
                    "focus": string,
                    "content": string
                }}
            ]
        }}
        """
        
    def _create_optimization_prompt(
        self,
        campaign_data: Dict[str, Any],
        performance_metrics: Dict[str, Any]
    ) -> str:
        return f"""
        Analyze the following campaign data and metrics to provide optimization recommendations:
        
        Campaign Data:
        {json.dumps(campaign_data, indent=2)}
        
        Performance Metrics:
        {json.dumps(performance_metrics, indent=2)}

        Provide the response in JSON format with the following structure:
        {{
            "performance_analysis": {{
                "strengths": [string],
                "weaknesses": [string],
                "opportunities": [string]
            }},
            "optimization_recommendations": [
                {{
                    "area": string,
                    "recommendation": string,
                    "expected_impact": string,
                    "implementation_complexity": string,
                    "priority": string
                }}
            ],
            "targeting_adjustments": {{
                "audience_segments": [string],
                "exclusions": [string],
                "bid_adjustments": object
            }},
            "creative_recommendations": [
                {{
                    "element": string,
                    "current_version": string,
                    "recommended_changes": string,
                    "rationale": string
                }}
            ]
        }}
        """
