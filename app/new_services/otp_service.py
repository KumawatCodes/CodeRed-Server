import random
from app.core.redis import redis_client

OTP_EXPIRY = 300
RATE_LIMIT = 30

def generate_otp():
    return str(random.randint(100000, 999999))


async def send_otp_logic(email: str):
    rate_key = f"otp_limit:{email}"

    # ✅ FIX 1: add await
    if await redis_client.exists(rate_key):
        return False, "Wait before requesting again"

    otp = generate_otp()

    key = f"otp:{email}"

    # ✅ FIX 2: add await
    await redis_client.setex(key, OTP_EXPIRY, otp)

    # ✅ FIX 3: correct function name + await
    await redis_client.setex(rate_key, RATE_LIMIT, "1")

    return True, otp


async def verify_otp_logic(email: str, user_otp: str):
    key = f"otp:{email}"

    stored = await redis_client.get(key)

    if not stored:
        return False, "OTP expired"

    if stored != user_otp:
        return False, "Invalid OTP"

    await redis_client.delete(key)

    return True, "Verified"