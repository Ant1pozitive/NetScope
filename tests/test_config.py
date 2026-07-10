from netscope.config import CONFIG, LoggingConfig


def test_replace_config():

    original = CONFIG.config

    CONFIG.replace(
        logging=LoggingConfig(
            level="DEBUG",
        )
    )

    assert CONFIG.config.logging.level == "DEBUG"

    CONFIG.reset()

    assert CONFIG.config == original