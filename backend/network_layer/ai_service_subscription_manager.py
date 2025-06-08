import logging
from utils.class_utils import generate_short_hash
from typing import Optional


logger = logging.getLogger(__name__)


class AIServiceSubscription:

    def __init__(
        self,
        sub_manager,
        ai_service_name: str,
        ai_service_data: dict,
        ue_id_list: list[str],
    ):
        self.sub_manager = sub_manager
        self.ai_service_name = ai_service_name
        self.ai_service_data = ai_service_data
        self.ue_id_list = ue_id_list
        self.subscription_id = generate_short_hash()

    @property
    def base_station_list(self):
        return self.sub_manager.base_station_list

    @property
    def cell_list(self):
        return self.sub_manager.cell_list

    @property
    def ue_list(self):
        return self.sub_manager.ue_list

    def __repr__(self):
        return (
            f"AIServiceSubscription(ai_service_name={self.ai_service_name}, "
            f"ue_id_list={self.ue_id_list}, subscription_id={self.subscription_id})"
        )

    def to_json(self) -> dict:
        return {
            "ai_service_name": self.ai_service_name,
            "ue_id_list": self.ue_id_list,
            "subscription_id": self.subscription_id,
        }

    def step(self):
        logger.info(
            f"Stepping through AI service subscription {self.subscription_id} for service {self.ai_service_name} with UEs {self.ue_id_list}"
        )
        # manage the current AI service subscription
        # for each base station,
        #   if there are any subscribing UEs connected to it
        #       if the AI service has not started.
        #           try to start the AI service at the edge cluster of the base station
        #           configure the local breakout and start the QoS monitoring xApp
        #       else
        #           do nothing
        #   else:
        #       if the AI service has started
        #           stop the AI service at the edge cluster of the base station,
        #           clean the local breakout rules and stop the QoS monitoring xApp
        for base_station in self.base_station_list.values():
            found_subscribing_ue = None
            for ue_imsi in self.ue_id_list:
                if ue_imsi in base_station.ue_registry:
                    found_subscribing_ue = ue_imsi
                    break
            logger.info(
                f"Base station {base_station.bs_id} found subscribing UE: {found_subscribing_ue}"
            )
            if found_subscribing_ue:
                logger.info(
                    f"getting or creating AI service deployment for subscription {self.subscription_id} at base station {base_station.bs_id}"
                )
                error, ai_service_deployment = (
                    base_station.edge_server.get_or_create_ai_service_deployment(self)
                )
                if error:
                    logger.error(
                        f"Failed to get or create AI service deployment for subscription {self.subscription_id}: {error}"
                    )
                else:
                    logger.info(
                        f"AI service deployment for subscription {self.subscription_id} is ready. Container name: {ai_service_deployment["container_name"]}"
                    )
            else:
                logger.info(
                    f"No subscribing UEs found at base station {base_station.bs_id} for subscription {self.subscription_id}. Stopping AI service if it is running."
                )
                # base_station.edge_server.stop_ai_service_deployment(self)


class AIServiceSubscriptionManager:
    def __init__(self, ric=None):
        self.ric = ric
        self.subscriptions = {}

    @property
    def base_station_list(self):
        return self.ric.base_station_list

    @property
    def cell_list(self):
        return self.ric.cell_list

    @property
    def ue_list(self):
        return self.ric.ue_list

    def create_subscription(
        self, ai_service_name: str, ai_service_data, ue_id_list: list[str]
    ) -> AIServiceSubscription:
        # check if the AI service subscription has already be created by matching the AI service name and UE IDs
        for subscription in self.subscriptions.values():
            if subscription.ai_service_name == ai_service_name and set(
                subscription.ue_id_list
            ) == set(ue_id_list):
                logger.info(
                    f"AI service subscription already exists: {subscription.subscription_id}"
                )
                return subscription
        subscription = AIServiceSubscription(
            self, ai_service_name, ai_service_data, ue_id_list
        )
        self.subscriptions[subscription.subscription_id] = subscription
        logger.info(
            f"Created AI service subscription: {subscription.subscription_id} for service {ai_service_name} with UEs {ue_id_list}"
        )
        return subscription

    def get_subscription(self, subscription_id: str) -> Optional[AIServiceSubscription]:
        return self.subscriptions.get(subscription_id, None)

    def delete_subscription(self, subscription_id: str) -> bool:
        if subscription_id in self.subscriptions:
            del self.subscriptions[subscription_id]
            return True
        return False

    def list_subscriptions(self) -> list[AIServiceSubscription]:
        return list(self.subscriptions.values())

    def to_json(self) -> dict:
        return {
            "subscriptions": [
                {
                    "ai_service_name": sub.ai_service_name,
                    "ue_id_list": sub.ue_id_list,
                    "subscription_id": sub.subscription_id,
                }
                for sub in self.subscriptions.values()
            ]
        }

    def step(self):
        for subscription in self.subscriptions.values():
            subscription.step()
