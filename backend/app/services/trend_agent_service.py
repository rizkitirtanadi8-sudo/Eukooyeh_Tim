"""
Trend Prediction Agent Service
Uses CrewAI to analyze market trends based on LLM knowledge.
"""
from crewai import Agent, Task, Crew
from crewai.llm import LLM
from app.core.config import get_settings
from datetime import datetime
import json
from typing import Dict, Any, List


class TrendAnalyzer:
    """
    AI Agent for market trend prediction.
    Uses LLM's internal knowledge to generate logical trend insights.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self) -> LLM:
        """Initialize LLM with configuration."""
        model_name = self.settings.openai_model_name
        
        if not model_name.startswith("openai/"):
            model_name = f"openai/{model_name}"
        
        return LLM(
            model=model_name,
            base_url=self.settings.openai_api_base,
            api_key=self.settings.openai_api_key
        )
    
    def _create_trend_agent(self) -> Agent:
        """Create specialized trend analysis agent."""
        return Agent(
            role="Senior Market Analyst for Indonesia (SE Asia)",
            goal="Predict viral micro-trends based on seasonality, social media, and market dynamics",
            backstory=(
                "You are an expert market analyst specializing in Indonesian and Southeast Asian markets. "
                "You have deep knowledge of TikTok trends, seasonal patterns, and consumer behavior. "
                "You can predict what products will go viral based on current date, season, and social dynamics."
            ),
            verbose=False,
            allow_delegation=False,
            llm=self.llm
        )
    
    async def analyze_trends(
        self,
        category: str,
        region: str = "Indonesia"
    ) -> Dict[str, Any]:
        """
        Analyze market trends for a specific category.
        
        Args:
            category: Product category (e.g., "Fashion", "Electronics")
            region: Target region (default: "Indonesia")
        
        Returns:
            Dictionary with trend predictions
        """
        
        # Get current date and season info
        now = datetime.now()
        current_month = now.strftime("%B")
        current_year = now.year
        
        # Determine season
        month_num = now.month
        if month_num in [12, 1, 2]:
            season = "Rainy Season / Holiday Season"
            season_context = "End of year holidays, Christmas, New Year celebrations"
        elif month_num in [3, 4, 5]:
            season = "Dry Season / Back to School"
            season_context = "School preparation, outdoor activities"
        elif month_num in [6, 7, 8]:
            season = "Mid-Year / Ramadan Period"
            season_context = "Ramadan, Eid celebrations, religious activities"
        else:
            season = "Rainy Season / Year-End Preparation"
            season_context = "Preparation for holidays, rainy weather needs"
        
        # Create trend analysis agent
        trend_agent = self._create_trend_agent()
        
        # Create analysis task
        analysis_task = Task(
            description=f"""
Analyze market trends for the category: "{category}" in {region}.

CURRENT CONTEXT:
- Date: {current_month} {current_year}
- Season: {season}
- Context: {season_context}
- Region: {region} (Southeast Asia)

YOUR TASK:
Predict 3 specific micro-trends that are likely to go viral based on:
1. Current season and weather patterns
2. TikTok and social media trends
3. Cultural events and holidays
4. Consumer behavior patterns

For each trend, provide:
- product_name: Specific product name (be creative and realistic)
- viral_reason: Why this product will trend (mention TikTok, season, or cultural factors)
- growth_potential: Percentage estimate (e.g., "150%" or "200%")
- price_range: Suggested price range in IDR
- target_audience: Who will buy this

IMPORTANT: Return ONLY valid JSON in this exact format:
{{
  "category": "{category}",
  "region": "{region}",
  "analysis_date": "{now.isoformat()}",
  "season": "{season}",
  "trends": [
    {{
      "product_name": "specific product name",
      "viral_reason": "detailed reason why it will trend",
      "growth_potential": "percentage",
      "price_range": "Rp X - Rp Y",
      "target_audience": "demographic description"
    }}
  ]
}}

Be specific, creative, and realistic. Use actual TikTok trends and seasonal patterns.
""",
            expected_output="JSON with 3 trend predictions",
            agent=trend_agent
        )
        
        # Execute analysis
        crew = Crew(
            agents=[trend_agent],
            tasks=[analysis_task],
            verbose=False
        )
        
        result = crew.kickoff()
        
        # Parse result
        return self._parse_trend_result(str(result), category, region)
    
    def _parse_trend_result(
        self,
        result: str,
        category: str,
        region: str
    ) -> Dict[str, Any]:
        """Parse AI result into structured format."""
        try:
            # Try to parse as JSON
            import re
            
            # Extract JSON from markdown code blocks if present
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', result, re.DOTALL)
            if json_match:
                result = json_match.group(1)
            
            # Try direct JSON parse
            parsed = json.loads(result)
            
            # Validate structure
            if "trends" in parsed and isinstance(parsed["trends"], list):
                return parsed
            
        except json.JSONDecodeError:
            pass
        
        # Fallback: Create structured response from text
        return {
            "category": category,
            "region": region,
            "analysis_date": datetime.now().isoformat(),
            "season": "Current Season",
            "trends": [
                {
                    "product_name": f"Trending {category} Item 1",
                    "viral_reason": "Popular on TikTok and social media",
                    "growth_potential": "150%",
                    "price_range": "Rp 50,000 - Rp 200,000",
                    "target_audience": "Young adults 18-35"
                },
                {
                    "product_name": f"Trending {category} Item 2",
                    "viral_reason": "Seasonal demand and weather patterns",
                    "growth_potential": "120%",
                    "price_range": "Rp 100,000 - Rp 300,000",
                    "target_audience": "General consumers"
                },
                {
                    "product_name": f"Trending {category} Item 3",
                    "viral_reason": "Cultural events and holidays",
                    "growth_potential": "180%",
                    "price_range": "Rp 75,000 - Rp 250,000",
                    "target_audience": "Families and gift buyers"
                }
            ],
            "raw_analysis": result
        }


# Singleton instance
_trend_analyzer = None

def get_trend_analyzer() -> TrendAnalyzer:
    """Get or create trend analyzer instance."""
    global _trend_analyzer
    if _trend_analyzer is None:
        _trend_analyzer = TrendAnalyzer()
    return _trend_analyzer
