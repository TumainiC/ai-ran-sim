from utils import parse_memory_usage_string, start_ai_service_with_docker
import logging

logger = logging.getLogger(__name__)


class EdgeServer:
    def __init__(self, base_station, edge_server_init_data):
        self.base_station = base_station
        self.edge_id = base_station.bs_id + "_edge"
        self.node_id = edge_server_init_data.get("node_id", "default_edge_server_node")
        self.device_type = edge_server_init_data.get("device_type", "DeviceType.CPU")
        self.cpu_memory_GB = edge_server_init_data.get("cpu_memory_GB", 10.0)
        self.device_memory_GB = edge_server_init_data.get("device_memory_GB", 0.0)

        self.ai_service_deployments = {}

    @property
    def available_cpu_memory_GB(self):
        cpu_memory_used_GB = 0
        for deployed_ai_service in self.ai_service_deployments.values():
            cpu_memory_used_GB += deployed_ai_service.get(
                "edge_specific_cpu_memory_usage_GB", 0.0
            )
        return self.cpu_memory_GB - cpu_memory_used_GB

    @property
    def available_device_memory_GB(self):
        device_memory_used_GB = 0
        for deployed_ai_service in self.ai_service_deployments.values():
            device_memory_used_GB += deployed_ai_service.get(
                "edge_specific_device_memory_usage_GB", 0.0
            )

        return self.device_memory_GB - device_memory_used_GB

    def format_container_name(self, ai_service_subscription):
        """
        Format the container name for the AI service deployment.

        Args:
            ai_service_subscription (AIServiceSubscription): The AI service subscription object.

        Returns:
            str: The formatted container name.
        """
        return f"{self.edge_id}_{ai_service_subscription.subscription_id}_{ai_service_subscription.ai_service_name.replace(' ', '_')}"

    def get_or_create_ai_service_deployment(self, ai_service_subscription):
        """
        Get or create an AI service deployment for the given AI service subscription.
        AI service is per subscription basis for the moment, until in the future we support multiple deployments per subscription to enable load balancing.

        returns:
            error (str): Error message if any, otherwise None.
            ai_service_deployment (dict): The AI service deployment data if created or found, otherwise None.
        """
        subscription_id = ai_service_subscription.subscription_id
        if subscription_id in self.ai_service_deployments:
            return (
                None,
                self.ai_service_deployments[subscription_id],
            )

        ai_service_name = ai_service_subscription.ai_service_name

        # check if the edge server has enough resources to deploy the AI serivce
        edge_specific_profile = None
        for profile in ai_service_subscription.ai_service_data["profiles"]:
            if profile["node_id"] == self.node_id:
                edge_specific_profile = profile
                break

        if edge_specific_profile is None:
            # the AI service has not been tested on this edge server yet
            return (
                f"This {ai_service_name} AI service is not compatible with the edge server {self.edge_id}.",
                None,
            )
        edge_specific_cpu_memory_usage_GB = parse_memory_usage_string(
            edge_specific_profile.get("idle_container_cpu_memory_usage")
        )

        edge_specific_device_memory_usage_GB = parse_memory_usage_string(
            edge_specific_profile.get("idle_container_device_memory_usage")
        )

        available_cpu_memory_GB = self.available_cpu_memory_GB
        available_device_memory_GB = self.available_device_memory_GB

        if (
            edge_specific_cpu_memory_usage_GB > available_cpu_memory_GB
            or edge_specific_device_memory_usage_GB > available_device_memory_GB
        ):
            return (
                f"Not enough resources to deploy {ai_service_name} AI service on the edge server {self.edge_id}.",
                None,
            )

        # deploy the AI service and return the deployment data
        ai_service_data = ai_service_subscription.ai_service_data
        # AI service docker image repository url
        # e.g., docker.io/cranfield6g/cranfield-edge-trpakov-vit-face-expression
        image_repository_url = ai_service_data["image_repository_url"]

        container_name = self.format_container_name(ai_service_subscription)
        error, ai_service_endpoint = start_ai_service_with_docker(
            ai_service_image_url=image_repository_url,
            container_name=container_name,
        )

        if error:
            return (
                f"Failed to start the AI service {ai_service_name} on the edge server {self.edge_id}: {error}",
                None,
            )

        self.ai_service_deployments[subscription_id] = {
            "ai_service_subscription": ai_service_subscription,
            "base_station_id": self.base_station.bs_id,
            "edge_id": self.edge_id,
            "node_id": self.node_id,
            "ai_service_endpoint": ai_service_endpoint,
            "ai_service_data": ai_service_data,
            "image_repository_url": image_repository_url,
            "container_name": self.format_container_name(ai_service_subscription),
            "edge_specific_cpu_memory_usage_GB": edge_specific_cpu_memory_usage_GB,
            "edge_specific_device_memory_usage_GB": edge_specific_device_memory_usage_GB,
        }

        logger.info(
            f"Deployed AI service {ai_service_name} on edge server {self.edge_id} with endpoint {ai_service_endpoint}."
        )
        return None, self.ai_service_deployments[subscription_id]
