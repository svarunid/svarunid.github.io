import uuid

from fastapi import Request


def generate_device_uid(request: Request) -> str:
  """Generate a unique identifier based on device-level identifiers only."""
  ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
  if not ip: ip = request.client.host if request.client else "unknown"

  platform = request.headers.get("sec-ch-ua-platform", "")
  is_mobile = request.headers.get("sec-ch-ua-mobile", "")

  return str(uuid.uuid5(uuid.NAMESPACE_DNS, "|".join([ip, platform, is_mobile]).encode()))
