import bot
import logging


logger = logging.getLogger(str(__name__).upper())


def main():
    logger.info("Starting...")
    bot.start()


if __name__ == "__main__":
    main()
