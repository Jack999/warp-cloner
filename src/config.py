from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

class Settings(BaseSettings):
    model_config =  SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    BASE_KEYS: list[str] = Field(
        validation_alias='BASE_KEYS',
        default=[
            '6S5P3gn0-14e7O3UH-P3C8F51n',
            '60F1U3oM-4Y2w8K1G-128AE6sy',
            'C29u3T7F-53YB60rk-0y453JZj',
            '6324VIUl-Ph0t3M52-981ZbpN0',
            'zbP702S4-6Fe4H2z9-40pwoI37',
            'e4LB5T32-594ZWT6q-2H4zfS73',
            '65m4EI7k-4W5Vpq30-0zVtF643',
            '6pT97C4s-2P7MCD45-ux90X58I',
            '8Rw9LA63-07rWqp26-3lzk09F8',
            'uQh6907W-9lrV6Z02-8Y4oT19I',
        ]
    )
    THREADS_COUNT: int = Field(validation_alias='THREADS_COUNT', default=1)
    PROXY_FILE: str | None = Field(validation_alias='PROXY_FILE', default=None)
    DEVICE_MODELS: list[str] = Field(validation_alias='DEVICE_MODELS', default=[])
    WEBHOOK_KEY_URL: str | None = Field(validation_alias='WEBHOOK_KEY_URL', default=None)
    SAVE_WIREGUARD_VARIABLES: bool = Field(validation_alias='SAVE_WIREGUARD_VARIABLES', default=False)
    DELAY: int = Field(validation_alias='DELAY', default=40)
    OUTPUT_FILE: str = Field(validation_alias='OUTPUT_FILE', default='output.txt')
    OUTPUT_FORMAT: str = Field(validation_alias='OUTPUT_FORMAT', default='{key} | {referral_count} GB')
    RETRY_COUNT: int = Field(validation_alias='RETRY_COUNT', default=3)


config = Settings()
