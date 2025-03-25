from fastapi import Query

PAGE_SIZE_DEFAULT: int = 50
PAGE_SIZE_MIN: int = 1

PAGE_NUMBER: int = 1


class PaginationParams:
    def __init__(
            self,
            page_size: int = Query(
                PAGE_SIZE_DEFAULT,
                ge=PAGE_SIZE_MIN,
                description="Количество результатов на странице.",
            ),
            page_number: int = Query(
                PAGE_NUMBER, ge=PAGE_NUMBER, description="Номер страницы для пагинации."
            ),
    ):
        self.page_number = page_number
        self.page_size = page_size
