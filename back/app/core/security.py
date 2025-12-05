from authx import AuthX, AuthXConfig

config = AuthXConfig()
config.JWT_SECRET_KEY = "SECRET_KEY"
config.JWT_ACCESS_COOKIE_NAME = "MY_COOKIE"
config.JWT_TOKEN_LOCATION = ["cookies"]

security = AuthX(config = config)
