from rest_framework.pagination import PageNumberPagination


class CustomLimitPaginator(PageNumberPagination):
    """Пагинатор установливает размер страницы
    через параметр запроса 'limit'."""
    page_size_query_param = 'limit'
