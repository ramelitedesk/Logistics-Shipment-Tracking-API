from app.integrations.carriers.base import CarrierAdapter
from app.integrations.carriers.custom import CustomCarrierAdapter


def get_carrier_adapter(carrier_code: str) -> CarrierAdapter:
    """
    Return the appropriate adapter for a carrier.
    """

    normalized_code = carrier_code.upper()

    if normalized_code == "CUSTOM":
        return CustomCarrierAdapter()

    raise ValueError(
        f"No adapter configured for carrier: {carrier_code}"
    )