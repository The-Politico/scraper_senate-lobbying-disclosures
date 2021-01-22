def parse_safe_query_dict(raw_dict):
    return "&".join([f"{k}={v}" for k, v in raw_dict.items()])
