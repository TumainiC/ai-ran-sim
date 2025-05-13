from enum import Enum


class Relationship(Enum):
    ATTRIBUTE_OF = "attribute_of"
    HAS_ATTRIBUTE = "has_attribute"
    RELATED_STANDARD = "related_standard"
    CONSTRAINED_BY = "constrained_by"
    DEPENDS_ON = "depends_on"
    DERIVED_FROM = "derived_from"
    AFFECTS = "affects"
    BELONGS_TO = "belongs_to"
