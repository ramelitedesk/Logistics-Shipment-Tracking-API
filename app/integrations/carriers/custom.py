from app.integrations.carriers.base import CarrierAdapter


class CustomCarrierAdapter(CarrierAdapter):
    """
    Default adapter for custom or internal carrier integrations.
    """

    def create_shipment(
        self,
        shipment_data: dict,
    ) -> dict:
        return {
            "success": True,
            "message": "Shipment creation request prepared",
            "shipment_data": shipment_data,
        }

    def get_tracking(
        self,
        tracking_number: str,
    ) -> dict:
        return {
            "success": True,
            "tracking_number": tracking_number,
            "message": "Tracking request prepared",
        }

    def cancel_shipment(
        self,
        tracking_number: str,
    ) -> dict:
        return {
            "success": True,
            "tracking_number": tracking_number,
            "message": "Shipment cancellation request prepared",
        }

    def generate_label(
        self,
        tracking_number: str,
    ) -> dict:
        return {
            "success": True,
            "tracking_number": tracking_number,
            "message": "Label generation request prepared",
        }