# TV in Stasera

This project is a Telegram bot that notifies users about Italian TV programs scheduled for the day. Users can set notification times, manage a blacklist of channels they don't want to receive notifications for, and get detailed information about specific TV programs.

## Features

- **Daily Notifications**: Users receive daily notifications about TV programs at their preferred time.
- **Blacklist Management**: Users can manage a blacklist of channels they don't want to receive notifications for.
- **Program Information**: Users can get detailed information about specific TV programs, including descriptions, trailers, and images.

## Commands

- `/start`: Register the user and start receiving notifications.
- `/help`: Display help information about available commands.
- `/cambio <ora>:<minuto>`: Change the notification time.
- `/rottura`: Check the current notification time.
- `/avast`: Stop receiving notifications.
- `/riattiva`: Resume receiving notifications at the default time (14:00).
- `/canale <numero>`: Get information about a specific channel.
- `/set_blacklist`: Manage the blacklist of channels.

## Setup

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
    ```

4. Run the bot:
    ```sh
    python bot.py
    ```

## Files

- `bot.py`: Main bot implementation.
- `get_stesera.py`: Script to fetch TV program data and save it to `stasera.json`.
- `canali.json`: JSON file containing channel information.
- `stasera.json`: JSON file containing the fetched TV program data.
- `requirements.txt`: List of required Python packages.
- `README.md`: Project documentation.

## get_stesera.py

The `get_stesera.py` script scrapes the website "staseraintv.com" to fetch TV program data for various Italian channels. It collects information such as the title, description, additional info, trailer link, and image for each TV program. The data is then saved to `stasera.json` for use by the Telegram bot.

## License

This project is licensed under the MIT License.