import requests

RATES_URL = "https://open.er-api.com/v6/latest/USD"
TIMEOUT_SECONDS = 5


class ExternalApiError(Exception):
    """An error whose message is safe to show to workflow users."""


def get_usd_inr_rate(url: str = RATES_URL, timeout: float = TIMEOUT_SECONDS) -> float:
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        return float(data["rates"]["INR"])
    except requests.Timeout as exc:
        raise ExternalApiError(
            "The exchange-rate service took too long to respond. Please try again."
        ) from exc
    except requests.HTTPError as exc:
        raise ExternalApiError(
            f"The exchange-rate service returned an error ({exc.response.status_code})."
        ) from exc
    except requests.RequestException as exc:
        raise ExternalApiError("Could not reach the exchange-rate service.") from exc
    except (KeyError, ValueError, TypeError) as exc:
        raise ExternalApiError("The exchange-rate service sent an unexpected response.") from exc