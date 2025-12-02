# Traefik Pulse Logger

A real-time monitoring and logging dashboard for Traefik, built with Python (Flask) and Docker. This project captures Traefik access logs, stores them in a SQLite database, and visualizes the data in a modern, dark-themed dashboard.

## Features

*   **Real-time Dashboard**: View traffic stats and logs as they happen.
*   **Visualizations**:
    *   **Traffic Overview**: Line chart showing request volume over time.
    *   **Status Distribution**: Doughnut chart breaking down HTTP status codes (2xx, 4xx, 5xx).
*   **Detailed Logs**: Searchable table of recent requests with method, path, status, and duration.
*   **Time Filtering**: Select specific date and time ranges to analyze traffic.
*   **Docker Integration**: Fully containerized setup with Traefik and a demo service.

## Prerequisites

*   [Docker](https://www.docker.com/get-started)
*   [Docker Compose](https://docs.docker.com/compose/install/)

## Quick Start

1.  **Clone the repository** (if applicable) or navigate to the project directory.

2.  **Start the services**:
    ```bash
    docker-compose up -d --build
    ```

3.  **Access the Dashboard**:
    Open your browser and go to [http://localhost:5000](http://localhost:5000).
    
    *Alternatively, access via Traefik at [http://localhost](http://localhost) (if configured).*

4.  **Generate Traffic**:
    To see data in the dashboard, you need to generate some requests. The project includes a `whoami` service for this purpose.
    *   Visit [http://localhost/whoami](http://localhost/whoami) multiple times.
    *   Refresh the page or use a tool like `curl` or `ab` to generate load.

## Project Structure

```
.
├── app/
│   ├── static/         # CSS and JavaScript files
│   ├── templates/      # HTML templates
│   └── main.py         # Flask application logic
├── logs/               # Shared volume for Traefik access logs
├── docker-compose.yml  # Docker services configuration
├── Dockerfile          # Build instructions for the Logger app
└── requirements.txt    # Python dependencies
```

## Configuration

### Docker Compose
The `docker-compose.yml` defines three services:
*   **traefik**: The reverse proxy. It mounts the Docker socket and exposes ports 80 and 8080. It is configured to output access logs to `./logs/access.log`.
*   **whoami**: A simple echo server to test routing and generate logs.
*   **logger**: The custom Flask application that parses the logs and hosts the dashboard.

### Windows Users
If you are running Docker on Windows, you might need to adjust the Docker socket volume mount in `docker-compose.yml` if you encounter connection errors.
*   Default (Linux/Mac): `/var/run/docker.sock:/var/run/docker.sock`
*   Windows (Git Bash/MinGW): `//var/run/docker.sock:/var/run/docker.sock`

## Troubleshooting

*   **No logs appearing?**
    *   Ensure Traefik is running and accessible.
    *   Check if the `logs/access.log` file is being populated on your host machine.
    *   Verify that the `logger` service has read permissions for the log file.

*   **Traefik connection errors?**
    *   Check the Docker socket path in `docker-compose.yml` as mentioned in the Configuration section.

## License

MIT
