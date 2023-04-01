def get_future_value(start_year, future_year, value, factor):
    return round(value * (1 + factor) ** (future_year - start_year),0)
