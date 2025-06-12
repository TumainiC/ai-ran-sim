import os
import random

AI_SERVICE_UNDEPLOYMENT_COUNT_DOWN_STEPS = 20

AI_SERVICE_SAMPLE_REQUEST_DATA = []
AI_SERVICE_SAMPLE_IMAGE_FILES = ["puppy_in_cup.png", "dog_and_kitten.jpg"]


for image_file_name in AI_SERVICE_SAMPLE_IMAGE_FILES:
    with open(
        os.path.join(os.path.dirname(__file__), "..", "assets", image_file_name), "rb"
    ) as image_file:
        files = {
            "file": image_file.read(),
        }
        size = len(files["file"])
        AI_SERVICE_SAMPLE_REQUEST_DATA.append(
            {
                "files": files,
                "size": size,
                "name": image_file_name,
            }
        )


def get_random_ai_service_request_data():
    return random.choice(AI_SERVICE_SAMPLE_REQUEST_DATA)


def prepare_ai_service_sample_request(ai_service_name: str, ue_id: str, files: dict):
    return {
        "url": f"http://cranfield_6G.com/ai_services/{ai_service_name}",
        "data": {
            "ue_id": ue_id,
        },
        "files": files,
    }
