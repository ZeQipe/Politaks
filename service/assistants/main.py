
import openai
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from src.llm_utils import OpenAIAgent
from src.models import *
from src.settings import logger

app = FastAPI(
    title="Politaks assistants API",
    version="0.0.1",
)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

agent = OpenAIAgent()


@app.post(route1:="/api/v1/change/subdescription", response_model=SubDescriptionResponse)
async def change_subdescription_endpoint(request: SubDescriptionRequest):
    try:
        sub_description = await agent.get_sub_description(
            request.llm_model,
            request.domain,
            request.product_name,
            request.description,
            request.usage,
            request.seo_high_freq,
            request.seo_medium_freq,
            request.seo_low_freq,
        )

        return SubDescriptionResponse(
            sub_description=sub_description,
        )
    except openai.BadRequestError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route1} - {e.message}") from None
    except openai.AuthenticationError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route1} - {e.message}") from None
    except openai.PermissionDeniedError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route1} - {e.message}") from None
    except openai.NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route1} - {e.message}") from None
    except openai.ConflictError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route1} - {e.message}") from None
    except openai.UnprocessableEntityError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route1} - {e.message}") from None
    except openai.RateLimitError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route1} - {e.message}") from None
    except openai.APITimeoutError as e:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=f"Error - {route1} - {e.message}") from None
    except openai.APIConnectionError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Error - {route7} - {e.message}") from None
    except HTTPException as e:
        if f"Error - {route1}" in e.detail:
            logger.error(e.detail)
        else:
            logger.error(f"Error - {route1} - {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"Exception - {route1} - {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Exception - {route1} - {e}") from e


@app.post(route2:="/api/v1/change/description", response_model=DescriptionResponse)
async def change_description_endpoint(request: DescriptionRequest):
    try:
        description = await agent.get_description(
            request.llm_model,
            request.domain,
            request.product_name,
            request.description,
            request.usage,
            request.seo_high_freq,
            request.seo_medium_freq,
            request.seo_low_freq,
        )

        return DescriptionResponse(
            description=description,
        )
    except openai.BadRequestError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route2} - {e.message}") from None
    except openai.AuthenticationError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route2} - {e.message}") from None
    except openai.PermissionDeniedError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route2} - {e.message}") from None
    except openai.NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route2} - {e.message}") from None
    except openai.ConflictError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route2} - {e.message}") from None
    except openai.UnprocessableEntityError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route2} - {e.message}") from None
    except openai.RateLimitError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route2} - {e.message}") from None
    except openai.APITimeoutError as e:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=f"Error - {route2} - {e.message}") from None
    except openai.APIConnectionError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Error - {route7} - {e.message}") from None
    except HTTPException as e:
        if f"Error - {route2}" in e.detail:
            logger.error(e.detail)
        else:
            logger.error(f"Error - {route2} - {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"Exception - {route2} - {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Exception - {route2} - {e}") from e


@app.post(route3:="/api/v1/change/usage", response_model=UsageResponse)
async def change_usage_endpoint(request: UsageRequest):
    try:
        usage = await agent.get_usage(
            request.llm_model,
            request.domain,
            request.product_name,
            request.usage,
        )

        return UsageResponse(
            usage=usage,
        )
    except openai.BadRequestError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route3} - {e.message}") from None
    except openai.AuthenticationError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route3} - {e.message}") from None
    except openai.PermissionDeniedError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route3} - {e.message}") from None
    except openai.NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route3} - {e.message}") from None
    except openai.ConflictError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route3} - {e.message}") from None
    except openai.UnprocessableEntityError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route3} - {e.message}") from None
    except openai.RateLimitError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route3} - {e.message}") from None
    except openai.APITimeoutError as e:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=f"Error - {route3} - {e.message}") from None
    except openai.APIConnectionError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Error - {route7} - {e.message}") from None
    except HTTPException as e:
        if f"Error - {route3}" in e.detail:
            logger.error(e.detail)
        else:
            logger.error(f"Error - {route3} - {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"Exception - {route3} - {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Exception - {route3} - {e}") from e


@app.post(route4:="/api/v1/change/features", response_model=FeaturesResponse)
async def change_features_endpoint(request: FeaturesRequest):
    try:
        features = await agent.get_features(
            request.llm_model,
            request.domain,
            request.product_name,
            request.features,
        )

        return FeaturesResponse(
            features=features,
        )
    except openai.BadRequestError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route4} - {e.message}") from None
    except openai.AuthenticationError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route4} - {e.message}") from None
    except openai.PermissionDeniedError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route4} - {e.message}") from None
    except openai.NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route4} - {e.message}") from None
    except openai.ConflictError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route4} - {e.message}") from None
    except openai.UnprocessableEntityError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route4} - {e.message}") from None
    except openai.RateLimitError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route4} - {e.message}") from None
    except openai.APITimeoutError as e:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=f"Error - {route4} - {e.message}") from None
    except openai.APIConnectionError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Error - {route7} - {e.message}") from None
    except HTTPException as e:
        if f"Error - {route4}" in e.detail:
            logger.error(e.detail)
        else:
            logger.error(f"Error - {route4} - {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"Exception - {route4} - {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Exception - {route4} - {e}") from e


@app.post(route5:="/api/v1/create/previews", response_model=PreviewsResponse)
async def create_previews_endpoint(request: PreviewsRequest):
    try:
        preview = await agent.get_preview(
            request.llm_model,
            request.domain,
            request.product_name,
            request.description,
            request.usage,
            request.seo_high_freq,
            request.seo_medium_freq,
            request.seo_low_freq,
        )

        return PreviewsResponse(
            preview=preview,
        )
    except openai.BadRequestError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route5} - {e.message}") from None
    except openai.AuthenticationError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route5} - {e.message}") from None
    except openai.PermissionDeniedError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route5} - {e.message}") from None
    except openai.NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route5} - {e.message}") from None
    except openai.ConflictError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route5} - {e.message}") from None
    except openai.UnprocessableEntityError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route5} - {e.message}") from None
    except openai.RateLimitError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route5} - {e.message}") from None
    except openai.APITimeoutError as e:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=f"Error - {route5} - {e.message}") from None
    except openai.APIConnectionError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Error - {route7} - {e.message}") from None
    except HTTPException as e:
        if f"Error - {route5}" in e.detail:
            logger.error(e.detail)
        else:
            logger.error(f"Error - {route5} - {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"Exception - {route5} - {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Exception - {route5} - {e}") from e


@app.post(route6:="/api/v1/create/reviews", response_model=ReviewsResponse)
async def create_reviews_endpoint(request: ReviewsRequest):
    try:
        reviews = await agent.get_reviews(
            request.llm_model,
            request.product_name,
            request.description,
            request.usage,
            request.seo_high_freq,
            request.seo_medium_freq,
            request.seo_low_freq,
        )

        return ReviewsResponse(
            **reviews,
        )
    except openai.BadRequestError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route6} - {e.message}") from None
    except openai.AuthenticationError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route6} - {e.message}") from None
    except openai.PermissionDeniedError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route6} - {e.message}") from None
    except openai.NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route6} - {e.message}") from None
    except openai.ConflictError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route6} - {e.message}") from None
    except openai.UnprocessableEntityError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route6} - {e.message}") from None
    except openai.RateLimitError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route6} - {e.message}") from None
    except openai.APITimeoutError as e:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=f"Error - {route6} - {e.message}") from None
    except openai.APIConnectionError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Error - {route7} - {e.message}") from None
    except HTTPException as e:
        if f"Error - {route6}" in e.detail:
            logger.error(e.detail)
        else:
            logger.error(f"Error - {route6} - {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"Exception - {route6} - {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Exception - {route6} - {e}") from e


@app.post(route7:="/api/v1/create/work_results", response_model=WorkResultsResponse)
async def create_work_results_endpoint(
    llm_model: str = Form(...),
    domain: str = Form("main"),
    place_name: str = Form(...),
    location: str = Form(...),
    background_info: str = Form(...),
    products_name: str = Form(...),
    descriptions: str = Form(...),
    photo1: UploadFile|str = File(None),
    photo2: UploadFile|str = File(None),
):
    try:
        # Нормализуем domain
        if not domain or domain.strip() == "":
            domain = "main"
        
        photo1_content = None
        photo2_content = None
        if photo1:
            photo1_content = await photo1.read()
        if photo2:
            photo2_content = await photo2.read()

        work_results = await agent.get_work_results(
            llm_model,
            domain,
            place_name,
            location,
            background_info,
            products_name,
            descriptions,
            photo1_content,
            photo2_content,
        )

        return WorkResultsResponse(
            work_results=work_results,
        )
    except openai.BadRequestError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route7} - {e.message}") from None
    except openai.AuthenticationError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route7} - {e.message}") from None
    except openai.PermissionDeniedError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route7} - {e.message}") from None
    except openai.NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route7} - {e.message}") from None
    except openai.ConflictError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route7} - {e.message}") from None
    except openai.UnprocessableEntityError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route7} - {e.message}") from None
    except openai.RateLimitError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route7} - {e.message}") from None
    except openai.APITimeoutError as e:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=f"Error - {route7} - {e.message}") from None
    except openai.APIConnectionError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Error - {route7} - {e.message}") from None
    except HTTPException as e:
        if f"Error - {route7}" in e.detail:
            logger.error(e.detail)
        else:
            logger.error(f"Error - {route7} - {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"Exception - {route7} - {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Exception - {route7} - {e}") from e


@app.post(route8:="/api/v1/change/article", response_model=ChArticleResponse)
async def change_article_endpoint(request: ChArticleRequest):
    try:
        article = await agent.change_article(
            request.llm_model,
            request.title,
            request.article,
            request.seo_high_freq,
            request.seo_medium_freq,
            request.seo_low_freq,
        )

        return ChArticleResponse(
            article=article,
        )
    except openai.BadRequestError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route8} - {e.message}") from None
    except openai.AuthenticationError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route8} - {e.message}") from None
    except openai.PermissionDeniedError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route8} - {e.message}") from None
    except openai.NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route8} - {e.message}") from None
    except openai.ConflictError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route8} - {e.message}") from None
    except openai.UnprocessableEntityError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route8} - {e.message}") from None
    except openai.RateLimitError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route8} - {e.message}") from None
    except openai.APITimeoutError as e:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=f"Error - {route8} - {e.message}") from None
    except openai.APIConnectionError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Error - {route7} - {e.message}") from None
    except HTTPException as e:
        if f"Error - {route8}" in e.detail:
            logger.error(e.detail)
        else:
            logger.error(f"Error - {route8} - {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"Exception - {route8} - {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Exception - {route8} - {e}") from e


@app.post(route9:="/api/v1/create/article", response_model=ArticleResponse)
async def create_article_endpoint(request: ArticleRequest):
    try:
        article = await agent.get_article(
            request.llm_model,
            request.topic,
            request.comment,
            request.seo_high_freq,
            request.seo_medium_freq,
            request.seo_low_freq,
        )

        return ArticleResponse(
            article=article,
        )
    except openai.BadRequestError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route9} - {e.message}") from None
    except openai.AuthenticationError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route9} - {e.message}") from None
    except openai.PermissionDeniedError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route9} - {e.message}") from None
    except openai.NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route9} - {e.message}") from None
    except openai.ConflictError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route9} - {e.message}") from None
    except openai.UnprocessableEntityError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route9} - {e.message}") from None
    except openai.RateLimitError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route9} - {e.message}") from None
    except openai.APITimeoutError as e:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=f"Error - {route9} - {e.message}") from None
    except openai.APIConnectionError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Error - {route7} - {e.message}") from None
    except HTTPException as e:
        if f"Error - {route9}" in e.detail:
            logger.error(e.detail)
        else:
            logger.error(f"Error - {route9} - {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"Exception - {route9} - {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Exception - {route9} - {e}") from e


@app.post(route10:="/api/v1/change/tech_instruction", response_model=TechInstructionResponse)
async def change_tech_instruction_endpoint(request: TechInstructionRequest):
    try:
        tech_instruction = await agent.change_tech_instruction(
            request.llm_model,
            request.domain,
            request.tech_instruction,
            request.seo_high_freq,
            request.seo_medium_freq,
            request.seo_low_freq,
        )

        return TechInstructionResponse(
            tech_instruction=tech_instruction,
        )
    except openai.BadRequestError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route10} - {e.message}") from None
    except openai.AuthenticationError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route10} - {e.message}") from None
    except openai.PermissionDeniedError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route10} - {e.message}") from None
    except openai.NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route10} - {e.message}") from None
    except openai.ConflictError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route10} - {e.message}") from None
    except openai.UnprocessableEntityError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route10} - {e.message}") from None
    except openai.RateLimitError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route10} - {e.message}") from None
    except openai.APITimeoutError as e:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=f"Error - {route10} - {e.message}") from None
    except openai.APIConnectionError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Error - {route7} - {e.message}") from None
    except HTTPException as e:
        if f"Error - {route10}" in e.detail:
            logger.error(e.detail)
        else:
            logger.error(f"Error - {route10} - {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"Exception - {route10} - {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Exception - {route10} - {e}") from e


@app.post(route11:="/api/v1/change/category_description", response_model=CategoryDescriptionResponse)
async def change_category_description_endpoint(request: CategoryDescriptionRequest):
    try:
        category_description = await agent.change_category_description(
            request.llm_model,
            request.domain,
            request.category_description,
            request.seo_high_freq,
            request.seo_medium_freq,
            request.seo_low_freq,
        )

        return CategoryDescriptionResponse(
            category_description=category_description,
        )
    except openai.BadRequestError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route11} - {e.message}") from None
    except openai.AuthenticationError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route11} - {e.message}") from None
    except openai.PermissionDeniedError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route11} - {e.message}") from None
    except openai.NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route11} - {e.message}") from None
    except openai.ConflictError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route11} - {e.message}") from None
    except openai.UnprocessableEntityError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route11} - {e.message}") from None
    except openai.RateLimitError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Error - {route11} - {e.message}") from None
    except openai.APITimeoutError as e:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=f"Error - {route11} - {e.message}") from None
    except openai.APIConnectionError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Error - {route7} - {e.message}") from None
    except HTTPException as e:
        if f"Error - {route11}" in e.detail:
            logger.error(e.detail)
        else:
            logger.error(f"Error - {route11} - {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"Exception - {route11} - {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Exception - {route11} - {e}") from e


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=7999, workers=2)
