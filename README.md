# TV in Stasera

This project is a Telegram bot that notifies users about Italian TV programs scheduled for the day. Users can set notification times, manage a blacklist of channels they don't want to receive notifications for, and get detailed information about specific TV programs.

You can interact with the bot on Telegram at [@TVinStasera_bot](https://t.me/TVinStasera_bot).

## Features

- **Daily Notifications**: Users receive daily notifications about Italian TV programs at their preferred time.
- **Blacklist Management**: Users can manage a blacklist of channels they don't want to receive notifications for.
- **Program Information**: Users can get detailed information about specific TV programs, including descriptions, trailers, and images.
- **Preferences Management**: Users can add or remove preferences for specific TV programs.

## Commands

- `/start`: Register the user and start receiving notifications.
- `/cambio <ora>:<minuto>`: Change the notification time.
- `/rottura`: Check the current notification time.
- `/avast`: Stop receiving notifications.
- `/riattiva`: Resume receiving notifications at the default time (14:00).
- `/canale <numero>`: Get information about a specific channel.
- `/set_blacklist`: Manage the blacklist of channels.
- `/add_prefe`: Add a preference for specific TV programs.
- `/rem_prefe`: Remove a preference for specific TV programs.
- `/help`: Display help information about available commands.

## Setup

### Local Setup

1. Clone the repository:
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Set up environment variables:
    Create a `.env` file with the following content:
    ```env
    BOT_TOKEN=<your-telegram-bot-token>
    API_ID=<your-telegram-api-id>
    API_HASH=<your-telegram-api-hash>
    DIR=/usr/src/app
    ```

4. Run the bot:
    ```sh
    python bot.py
    ```

### Docker Setup

1. Clone the repository:
    ```sh
    git clone https://github.com/lucaluisi/TVinStasera.git
    cd TVinStasera/
    ```

2. Create a `.env` file with the following content:
    ```env
    BOT_TOKEN=<your-telegram-bot-token>
    API_ID=<your-telegram-api-id>
    API_HASH=<your-telegram-api-hash>
    DIR=/usr/src/app
    ```

3. Run Docker Compose:
    ```sh
    docker-compose up -d
    ```

## Files

- `bot.py`: Main bot implementation.
- `get_stesera.py`: Script to fetch TV program data and save it to `stasera.json`.
- `canali.json`: JSON file containing channel information.
- `stasera.json`: JSON file containing the fetched TV program data.
- `requirements.txt`: List of required Python packages.
- `Dockerfile`: Docker configuration file.
- `docker-compose.yml`: Docker Compose configuration file.
- `start.sh`: Script to start the bot and cron job.
- `.env.example`: Example environment variables file.
- `README.md`: Project documentation.

## get_stesera.py

The `get_stesera.py` script scrapes the website "staseraintv.com" to fetch TV program data for various Italian channels. It performs the following steps:

1. Loads channel information from `canali.json`.
2. Iterates through multiple pages of the website to gather TV program data.
3. For each channel, it fetches the program details including the title, description, and additional information.
4. Fetches images for the programs from another website, "superguidatv.it".
5. Saves the collected data to `stasera.json` for use by the Telegram bot.

## License

This project is licensed under the MIT License.