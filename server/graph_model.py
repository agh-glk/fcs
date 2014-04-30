from bulbs.model import Node, Relationship
from bulbs.property import String, Integer, DateTime
from bulbs.utils import current_datetime


class Page(Node):
    element_type = 'page'

    url = String(nullable=False)
    depth = Integer()
    priority = Integer()
    fetch_time = DateTime(default=current_datetime, nullable=False)


class Link(Relationship):

    label = 'link'

    created = DateTime(default=current_datetime, nullable=False)