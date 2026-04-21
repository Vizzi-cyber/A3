"""
火山引擎 OpenAPI HMAC-SHA256 签名实现 (Signature Version 4)
与官方示例完全一致: https://www.volcengine.com/docs/6369/67268
"""
import hashlib
import hmac
import datetime


def _sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def _get_signature_key(key, date_stamp, region_name, service_name):
    k_date = _sign(key.encode("utf-8"), date_stamp)
    k_region = _sign(k_date, region_name)
    k_service = _sign(k_region, service_name)
    k_signing = _sign(k_service, "request")
    return k_signing


def sign_request(
    access_key: str,
    secret_key: str,
    method: str,
    uri: str,
    query: str,
    body: str,
    host: str = "visual.volcengineapi.com",
    region: str = "cn-north-1",
    service: str = "cv",
) -> dict:
    """
    为火山引擎请求生成签名并返回完整的请求头
    与官方 Python 示例逻辑完全一致
    """
    t = datetime.datetime.utcnow()
    current_date = t.strftime("%Y%m%dT%H%M%SZ")
    datestamp = t.strftime("%Y%m%d")

    canonical_uri = uri if uri.startswith("/") else "/" + uri
    canonical_querystring = query

    content_type = "application/json"
    payload_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()

    # 固定 signed_headers，与官方示例一致
    signed_headers = "content-type;host;x-content-sha256;x-date"
    canonical_headers = (
        f"content-type:{content_type}\n"
        f"host:{host}\n"
        f"x-content-sha256:{payload_hash}\n"
        f"x-date:{current_date}\n"
    )

    canonical_request = (
        method + "\n"
        + canonical_uri + "\n"
        + canonical_querystring + "\n"
        + canonical_headers + "\n"
        + signed_headers + "\n"
        + payload_hash
    )

    algorithm = "HMAC-SHA256"
    credential_scope = f"{datestamp}/{region}/{service}/request"
    string_to_sign = (
        algorithm + "\n"
        + current_date + "\n"
        + credential_scope + "\n"
        + hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
    )

    signing_key = _get_signature_key(secret_key, datestamp, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    authorization_header = (
        f"{algorithm} Credential={access_key}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )

    return {
        "X-Date": current_date,
        "Authorization": authorization_header,
        "X-Content-Sha256": payload_hash,
        "Content-Type": content_type,
        "host": host,
    }
