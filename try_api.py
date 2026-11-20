from services.externals import (
    RATES_URL,
    ExternalApiError,
    get_usd_inr_rate,
)


def attempt(label: str, **kwargs) -> None:
    try:
        rate = get_usd_inr_rate(**kwargs)
        print(f"{label}: OK, 1 USD = {rate:.2f} INR")
    except ExternalApiError as error:
        print(f"{label}: FAILED with message -> {error}")


attempt("1. Normal call")
attempt("2. Timeout (0.001s)", timeout=0.001)
attempt("3. Unreachable host", url="https://does-not-exist.invalid/")
attempt("4. HTTP error (404)", url="https://api.github.com/this-page-does-not-exist-xyz")
attempt(
    "5. Unexpected response",
    url="https://jsonplaceholder.typicode.com/todos/1"
)