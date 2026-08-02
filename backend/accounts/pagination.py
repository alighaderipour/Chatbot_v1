from rest_framework.pagination import PageNumberPagination


class UserPagination(PageNumberPagination):
    """
    Applied only to UserListCreateView (see views.py) — deliberately not set
    as the project-wide DEFAULT_PAGINATION_CLASS, since that would also
    paginate the conversations list and other endpoints that currently
    return a plain array and aren't built to handle a paginated response
    shape.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
