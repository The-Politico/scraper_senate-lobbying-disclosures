def querystring_to_dict(raw_url):
    return {
        k: v
        for d in [
            dict([_.split("=")]) for _ in raw_url.split("?")[1].split("&")
        ]
        for k, v in d.items()
    }
