response_codes = {
    200: "OK",
    400: "Bad request — the account does not comply with an acceptable format (i.e. it's an empty string)",
    401: "Unauthorised — either no API key was provided or it wasn't valid",
    403: "Forbidden — no user agent has been specified in the request",
    404: "Not Pwned",
    429: "Too many requests — the rate limit has been exceeded",
    503: "Service unavailable — usually returned by Cloudflare if the underlying service is not available",
}