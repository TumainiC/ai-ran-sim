import os

AI_SERVICE_UNDEPLOYMENT_COUNT_DOWN_STEPS = 20
AI_SERVICE_SAMPLE_REQUEST_FILES = {}
AI_SERVICE_SAMPLE_IMAGE_SIZE_BYTES = 0

with open(os.path.join(os.path.dirname(__file__), "puppy.png"), "rb") as image_file:
    AI_SERVICE_SAMPLE_REQUEST_FILES["file"] = image_file.read()
    AI_SERVICE_SAMPLE_IMAGE_SIZE_BYTES = len(AI_SERVICE_SAMPLE_REQUEST_FILES["file"])


def prepare_ai_service_sample_request(
    ai_service_name: str,
    ue_id: str,
):
    return {
        "url": f"http://cranfield_6G.com/ai_services/{ai_service_name}",
        "data": {
            "ue_id": ue_id,
        },
        "files": AI_SERVICE_SAMPLE_REQUEST_FILES,
    }
