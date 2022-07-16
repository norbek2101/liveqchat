from rest_framework import pagination


class CustomPagination(pagination.PageNumberPagination):
    page_size = 5
    max_page_size =10000
    # page_size_query_param = 'page_size'
    # page_query_param = 'p'


class ChatPagination(pagination.PageNumberPagination):
    page_size = 100
    max_page_size = 1000