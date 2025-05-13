from ..router import knowledge_getter, knowledge_explainer
from ..relationships import Relationship


@knowledge_getter(
    key="/sim/ue/{ue_imsi}/speed",
    tags=["UE", "mobility"],
    related=[("specs/3gpp/38.300/7.1.2", Relationship.RELATED_STANDARD)],
)
def ue_speed_getter(key, sim, params):
    return sim.ue_list[params["ue_imsi"]].speed


@knowledge_explainer(
    "/sim/ue/{ue_imsi}/speed",
    tags=["UE", "mobility"],
    related=[("specs/3gpp/38.300/7.1.2", Relationship.RELATED_STANDARD)],
)
def ue_speed_explainer(key, sim, params):
    speed = sim.ue_list[params["ue_imsi"]].speed
    if speed == 0:
        return "UE is not moving."
    return "UE is moving. Handover mechanism should be considered."
