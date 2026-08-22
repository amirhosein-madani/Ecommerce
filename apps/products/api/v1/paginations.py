from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    page_size = 9
    page_query_param = "page"
    max_page_size = 30
