from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # JWT签名密钥
    SECRET_KEY_ACCESS_API: str
    # JWT生成算法
    ALGORITHM: str
    # 访问TOKEN过期时间
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # 阿里百炼API_KEY
    DASHSCOPE_API_KEY: str
    # 阿里百炼URL
    DASHSCOPE_BASE_URL: str

    class Config:
        env_file = ".env"


settings = Settings()
