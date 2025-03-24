import logging
from dependency_injector.wiring import Provide, inject
from dependencies.container import ServiceContainer

from fastapi import APIRouter, Depends
from schemas.assistant_schema import AssistantYandexRequest, AssistantYandexResponse
from services.assistant import AssistantService
router = APIRouter()

@router.post("/alice_assistant", response_model=AssistantYandexResponse)
@inject
async def alice_assistant(
    request: AssistantYandexRequest,
    assistant_service:AssistantService = Depends(Provide[ServiceContainer.assistant_service]),
) -> AssistantYandexResponse:
    text = request.request.get("original_utterance", None)
    if text:
        response_text = await assistant_service.process_request(text)
        logging.info(f'response, {response_text}')
    else:
        response_text = "Задайте вопрос ?"

    return AssistantYandexResponse(
        version=request.version,
        session=request.session,
        response={"text": response_text, "end_session": False}
    )
