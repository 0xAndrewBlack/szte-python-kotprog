<h1 align="center">Market BOT</h1>

<p align="center">
Python Discord BOT for a simple market system. Made for a university course.
</p>

---

## Setup

### Requirements

- Discord Developer Portal Application [Guide](https://discordpy.readthedocs.io/en/stable/discord.html)
- Python 3.8 or higher
- [Prisma](https://www.prisma.io/) (required for database actions)
- [Docker](https://docs.docker.com/get-docker/) (optional)
- [Docker Compose](https://docs.docker.com/compose/install/) (optional)

### Installation

1. Clone the repository
2. Install the requirements with `pip install -r requirements.txt`
3. Invite your bot to your server
4. Start the database with `docker-compose up -d` or by running `docker-compose.yml` in your IDE.
5. Start the bot by running `python marketbot/main.py` or by clicking the play button in your IDE.
6. Have fun!

### Configuration

Copy the `.env.example` file to `.env` and fill in the required values.

## Usage

### Commands

| Command | Description |
| --- | --- |
| `/help` | Shows a list of all commands |
| `/marketplace` | Shows a list of all the available items in the market |
| `/shop <args>` | Create an order |
| `/delete <id>` | Deletes an order (you can only delete the ones you created) |
| `/update <id> <args>` | Updates an order (you can only update the ones you created) |
| `/ping` | Shows the latency of the bot |
| `/channel-info` | Shows information about a channel on the server |
| `/roll` | Rolls a random number |
| `/server-info` | Shows information about the server |

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---