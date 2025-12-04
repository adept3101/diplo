from authx import AuthX, AuthXConfig
import os

config = AuthXConfig()
config.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "SECRET KEY")
config.JWT_ACCESS_COOKIE_NAME = "MY_COOKIE"
config.JWT_TOKEN_LOCATION = ["cookies"]

security = AuthX(config = config)
