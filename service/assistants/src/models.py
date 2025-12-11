
from pydantic import BaseModel, Field


# "/api/v1/change/subdescription"
class SubDescriptionRequest(BaseModel):
    llm_model: str
    domain: str
    product_name: str
    description: str
    usage: str
    seo_high_freq: str = ""
    seo_medium_freq: str = ""
    seo_low_freq: str = ""

class SubDescriptionResponse(BaseModel):
    sub_description: str


# "/api/v1/change/description"
class DescriptionRequest(BaseModel):
    llm_model: str
    domain: str
    product_name: str
    description: str
    usage: str = None
    seo_high_freq: str = ""
    seo_medium_freq: str = ""
    seo_low_freq: str = ""

class DescriptionResponse(BaseModel):
    description: str


# "/api/v1/change/usage"
class UsageRequest(BaseModel):
    llm_model: str
    domain: str = None
    product_name: str | None = None
    usage: str

class UsageResponse(BaseModel):
    usage: str


# "/api/v1/change/features"
class FeaturesRequest(BaseModel):
    llm_model: str
    domain: str = None
    product_name: str | None = None
    features: str

class FeaturesResponse(BaseModel):
    features: str


# "/api/v1/create/preview"
class PreviewsRequest(BaseModel):
    llm_model: str
    domain: str
    product_name: str
    description: str
    usage: str = None
    seo_high_freq: str = ""
    seo_medium_freq: str = ""
    seo_low_freq: str = ""

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
    domain: str
    tech_instruction: str
    seo_high_freq: str = ""
    seo_medium_freq: str = ""
    seo_low_freq: str = ""

class TechInstructionResponse(BaseModel):
    tech_instruction: str


# "/api/v1/change/category_description"
class CategoryDescriptionRequest(BaseModel):
    llm_model: str
    domain: str
    category_description: str
    seo_high_freq: str = ""
    seo_medium_freq: str = ""
    seo_low_freq: str = ""

class CategoryDescriptionResponse(BaseModel):
    category_description: str
