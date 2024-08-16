from rest_framework.pagination import PageNumberPagination


class PostPagination(PageNumberPagination):
    page_query_param = 'posts_page'
    page_size = 2
    page_size_query_param = 'posts_page_size'
    max_page_size = 100


class CommentPagination(PageNumberPagination):
    page_query_param = 'comments_page'
    page_size = 5
    page_size_query_param = 'comments_page_size'
    max_page_size = 100
