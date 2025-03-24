from http import HTTPStatus

from fastapi import HTTPException


def http_exception(data, status: HTTPStatus, message: str):
    """
    Проверяет, является ли данные пустыми. Если да, то поднимает HTTPException
    с указанным статусом и сообщением.
    """
    if not data:
        raise HTTPException(status_code=status, detail=message)
