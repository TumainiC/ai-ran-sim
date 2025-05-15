from enum import Enum


class KnowledgeRelationship(Enum):
    ATTRIBUTE_OF = "attribute_of"
    HAS_ATTRIBUTE = "has_attribute"
    RELATED_STANDARD = "related_standard"
    CONSTRAINED_BY = "constrained_by"
    DEPENDS_ON = "depends_on"
    DERIVED_FROM = "derived_from"
    AFFECTS = "affects"
    BELONGS_TO = "belongs_to"
    USED_BY = "used_by"
    DETERMINED_IN_METHOD = "DETERMINED_IN_METHOD"
    ASSOCIATED_WITH = "associated_with"

    CALL_METHOD = "call_method"
    CALLED_IN_METHOD = "called_in_method"

    DETERMINE_ATTRIBUTE = "determine_attribute"
