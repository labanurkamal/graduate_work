from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from core.config import assistant_settings
from dependencies.container import ServiceContainer
from schemas.assistant_schema import (AssistantYandexRequest,
                                      AssistantYandexResponse, Card, Response)
from services.assistant import AssistantService

router = APIRouter()


@router.post(
    "/alice_assistant",
    response_model=AssistantYandexResponse,
    summary="Обработка запроса Яндекс.Алисы",
    description=(
            "Этот эндпоинт принимает запрос от Яндекс.Алисы, анализирует введенный пользователем текст "
            "и формирует ответ в зависимости от контекста. Если сессия новая, отправляется приветственное "
            "сообщение с карточкой, иначе запрос обрабатывается и возвращается соответствующий ответ."
    ),
)
@inject
async def alice_assistant(
        request: AssistantYandexRequest,
        assistant_service: AssistantService = Depends(
            Provide[ServiceContainer.assistant_service]
        ),
) -> AssistantYandexResponse:
    text = request.request.get("original_utterance", None)

    if request.session.get("new", False):
        response_text = (
            "Привет! Я могу рассказать о фильмах, актерах и режиссерах. "
            "Спроси, например: «Кто снял фильм Интерстеллар?» или «Какие фильмы у Тарантино?»"
        )
        card = Card(
            image_id=assistant_settings.card_image_id,
            title=assistant_settings.card_title,
            description=assistant_settings.card_description,
        )
    elif text:
        response_text = await assistant_service.process_request(text)
        card = None
    else:
        response_text = "Задайте вопрос ?"
        card = None

    return AssistantYandexResponse(
        version=request.version,
        session=request.session,
        response=Response(
            text=response_text, end_session=False, card=card
        ).model_dump(),
    )
