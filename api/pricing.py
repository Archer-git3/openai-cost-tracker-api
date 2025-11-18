# Ціни за 1 мільйон токенів
PRICING = {
    "gpt-4o-mini": {
        "input": 0.15,  # $0.15 за 1M вхідних
        "output": 0.60  # $0.60 за 1M вихідних
    }
}


def calculate_cost(model: str, input_tok: int, output_tok: int) -> float:
    rates = PRICING.get(model)
    if not rates:
        return 0.0

    input_cost = (input_tok / 1_000_000) * rates["input"]
    output_cost = (output_tok / 1_000_000) * rates["output"]

    return round(input_cost + output_cost, 8)