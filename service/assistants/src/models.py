
from pydantic import BaseModel, Field, field_validator


def normalize_domain(v):
    """Заменяет None или пустую строку на 'main'"""
    if v is None or v == "" or v.strip() == "":
        return "main"
    return v


# "/api/v1/change/subdescription"
class SubDescriptionRequest(BaseModel):
    llm_model: str
    domain: str = "main"
    product_name: str
    description: str
    usage: str
    seo_high_freq: str = ""
    seo_medium_freq: str = ""
    seo_low_freq: str = ""

    @field_validator('domain', mode='before')
    @classmethod
    def validate_domain(cls, v):
        return normalize_domain(v)

class SubDescriptionResponse(BaseModel):
    sub_description: str


# "/api/v1/change/description"
class DescriptionRequest(BaseModel):
    llm_model: str
    domain: str = "main"
    product_name: str
    description: str
    usage: str = None
    seo_high_freq: str = ""
    seo_medium_freq: str = ""
    seo_low_freq: str = ""

    @field_validator('domain', mode='before')
    @classmethod
    def validate_domain(cls, v):
        return normalize_domain(v)

class DescriptionResponse(BaseModel):
    description: str


# "/api/v1/change/usage"
class UsageRequest(BaseModel):
    llm_model: str
    domain: str = "main"
    product_name: str | None = None
    usage: str

    @field_validator('domain', mode='before')
    @classmethod
    def validate_domain(cls, v):
        return normalize_domain(v)

class UsageResponse(BaseModel):
    usage: str


# "/api/v1/change/features"
class FeaturesRequest(BaseModel):
    llm_model: str
    domain: str = "main"
    product_name: str | None = None
    features: str

    @field_validator('domain', mode='before')
    @classmethod
    def validate_domain(cls, v):
        return normalize_domain(v)

class FeaturesResponse(BaseModel):
    features: str


# "/api/v1/create/preview"
class PreviewsRequest(BaseModel):
    llm_model: str
    domain: str = "main"
    product_name: str
    description: str
    usage: str = None
    seo_high_freq: str = ""
    seo_medium_freq: str = ""
    seo_low_freq: str = ""

    @field_validator('domain', mode='before')
    @classmethod
    def validate_domain(cls, v):
        return normalize_domain(v)

class PreviewsResponse(BaseModel):
    preview: str


# "/api/v1/create/reviews"
class ReviewsRequest(BaseModel):
    llm_model: str
    product_name: str
    description: str
    usage: str = None
    seo_high_freq: str = ""
    seo_medium_freq: str = ""
    seo_low_freq: str = ""

class Review(BaseModel):
    author: str
    rating: int = Field(..., ge=1, le=5)
    experience_of_use: str
    pros: str
    cons: str
    review: str
class ReviewsResponse(BaseModel):
    reviews: list[Review]


# "/api/v1/create/work_results"
class WorkResultsResponse(BaseModel):
    work_results: str


# "/api/v1/change/article"
class ChArticleRequest(BaseModel):
    llm_model: str
    title: str
    article: str
    seo_high_freq: str = ""
    seo_medium_freq: str = ""
    seo_low_freq: str = ""

class ChArticleResponse(BaseModel):
    article: str


# "/api/v1/create/article"
class ArticleRequest(BaseModel):
    llm_model: str
    topic: str
    comment: str
    seo_high_freq: str = ""
    seo_medium_freq: str = ""
    seo_low_freq: str = ""

class ArticleResponse(BaseModel):
    article: str


# "/api/v1/change/instruction"
class TechInstructionRequest(BaseModel):
    llm_model: str
    domain: str = "main"
    tech_instruction: str
    seo_high_freq: str = ""
    seo_medium_freq: str = ""
    seo_low_freq: str = ""

    @field_validator('domain', mode='before')
    @classmethod
    def validate_domain(cls, v):
        return normalize_domain(v)

class TechInstructionResponse(BaseModel):
    tech_instruction: str


# "/api/v1/change/category_description"
class CategoryDescriptionRequest(BaseModel):
    llm_model: str
    domain: str = "main"
    category_description: str
    seo_high_freq: str = ""
    seo_medium_freq: str = ""
    seo_low_freq: str = ""

    @field_validator('domain', mode='before')
    @classmethod
    def validate_domain(cls, v):
        return normalize_domain(v)

class CategoryDescriptionResponse(BaseModel):
    category_description: str
