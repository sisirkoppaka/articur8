from bulbs.model import Node, Relationship
from bulbs.property import String, Integer, DateTime
from bulbs.utils import current_datetime

class Article(Node):
	element_type = "article"

	url = String(nullable=False)

class Referral(Relationship):
	label = "referral"
	