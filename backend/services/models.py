from enum import Enum
from typing import List, Optional, Literal, Dict
from pydantic import BaseModel, Field, HttpUrl, validator

# --- Enums ---

class PipelineStatus(str, Enum):
    INIT = "INIT"
    CLIENT_SUMMARY = "CLIENT_SUMMARY"
    RAG_STRATEGY = "RAG_STRATEGY"
    PLAN_GENERATED = "PLAN_GENERATED"
    PLAN_VALIDATED = "PLAN_VALIDATED"
    RESEARCH = "RESEARCH"
    OUTPUT_VALIDATED = "OUTPUT_VALIDATED"
    SHEET_WRITTEN = "SHEET_WRITTEN"
    ERROR = "ERROR"

class MatchType(str, Enum):
    EXACT = "Exact"
    PHRASE = "Phrase"
    BROAD = "Broad"

class IntentLevel(str, Enum):
    HIGH = "High"       # Ready to buy
    MEDIUM = "Medium"   # Researching
    LOW = "Low"         # Just browsing
    BRAND = "Brand"     # Navigational

# --- Stage 1: Client Understanding ---

class ClientSummary(BaseModel):
    business_name: str = Field(..., description="Name of the client business")
    business_type: str = Field(..., description="Type of business (e.g., Dentist, E-commerce, SaaS)")
    primary_goal: str = Field(..., description="Main conversion goal (e.g., Leads, Sales, Calls)")
    location: str = Field(..., description="Target geography (e.g., London, UK, Global)")
    pricing_tier: Literal["Budget", "Standard", "Premium", "Luxury"] = Field(..., description="Price positioning")
    unique_selling_points: List[str] = Field(..., description="List of 3-5 key USPs")
    target_audience: str = Field(..., description="Description of the ideal customer")
    language: str = Field(default="English", description="Primary language for keywords and ads (e.g., Danish, English, German)")
    website_url: Optional[str] = Field(None, description="The client's website URL")
    has_gsc_access: bool = Field(default=False, description="Whether we have access to Google Search Console")
    ga4_property_id: Optional[str] = Field(None, description="GA4 Property ID if available")

# --- Stage 2: RAG Query ---

class RAGQuery(BaseModel):
    layer: Literal["strategy", "rules", "examples"] = Field(..., description="Which knowledge layer to access")
    client_type: str = Field(..., description="Client category to match case studies")
    goal: str = Field(..., description="Campaign goal context")
    region: Optional[str] = Field(None, description="Region specific rules")

# --- Stage 3: Research Report ---

class ValidatedKeyword(BaseModel):
    keyword: str
    volume: int
    cpc: Optional[float]
    competition: Optional[str]
    source: Literal["gsc", "kp", "both"]
    clicks: Optional[int] = 0
    impressions: Optional[int] = 0

class ResearchReport(BaseModel):
    gsc_keywords: List[Dict] = [] # Raw GSC data
    kp_keywords: List[Dict] = []  # Raw KP data
    kp_source: Literal["url", "seeds", "both"]
    validated_keywords: List[ValidatedKeyword] = [] # Merged & Filtered
    suggested_themes: List[str] = [] # LLM generated themes from data
    language_used: str
    location_used: str
    data_sources_used: List[str]

# --- Stage 4: Structure Plan ---

class AdGroupPlan(BaseModel):
    name: str = Field(..., description="Name of the Ad Group (following naming conventions)")
    intent: IntentLevel = Field(..., description="Target intent level")
    match_strategy: Literal["Phrase", "Exact", "Mixed"] = Field(..., description="Match type strategy for this group")
    theme: str = Field(..., description="The core theme/topic of keywords in this group")
    selected_keywords: List[str] = Field(..., description="Keywords selected from research for this group")

class StructurePlan(BaseModel):
    campaign_name: str = Field(..., description="Proposed Campaign Name")
    ad_groups: List[AdGroupPlan] = Field(..., description="List of planned Ad Groups")
    naming_convention: str = Field(..., description="The naming convention used (e.g., 'mb | Generic | Search')")
    negative_keywords: List[str] = Field(default=[], description="Global negative keywords to apply")

# --- Stage 5: Final Output ---

class KeywordRow(BaseModel):
    campaign: str
    ad_group: str
    keyword: str
    match_type: MatchType
    intent: IntentLevel
    volume: int = Field(ge=0, description="Monthly search volume")
    cpc: Optional[float] = Field(None, description="Estimated CPC")
    final_url: str = Field(..., description="Final URL for the ad")
    url_status: Literal["Verified", "Needs Review"] = Field(..., description="Whether the URL was verified or generated")
    headline_1: str = Field(..., description="Primary Headline")
    headline_2: str = Field(..., description="Secondary Headline")
    description_1: str = Field(..., description="Main Description")
    
    @validator('match_type')
    def validate_match_type_logic(cls, v, values):
        return v

class CampaignOutput(BaseModel):
    run_id: str
    client_summary: ClientSummary
    structure_plan: StructurePlan
    keywords: List[KeywordRow]
    
    @validator('keywords')
    def validate_keywords_not_empty(cls, v):
        if not v:
            raise ValueError("Campaign output must contain at least one keyword.")
        return v
