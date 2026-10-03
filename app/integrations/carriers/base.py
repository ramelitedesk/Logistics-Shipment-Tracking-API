from abc import ABC, abstractmethod


class CarrierAdapter(ABC):
    """
    Base interface for all carrier integrations.
    """

    @abstractmethod
    def create_shipment(
        self,
        shipment_data: dict,
    ) -> dict:
        """
        Create a shipment with the external carrier.
        """
        raise NotImplementedError

    @abstractmethod
    def get_tracking(
        self,
        tracking_number: str,
    ) -> dict:
        """
        Retrieve tracking information from the carrier.
        """
        raise NotImplementedError

    @abstractmethod
    def cancel_shipment(
        self,
        tracking_number: str,
    ) -> dict:
        """
        Cancel a shipment with the carrier.
        """
        raise NotImplementedError

    @abstractmethod
    def generate_label(
        self,
        tracking_number: str,
    ) -> dict:
        """
        Generate a shipping label.
        """
        raise NotImplementedError