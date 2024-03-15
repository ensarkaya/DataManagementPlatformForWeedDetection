# Web-based Data Management Platform for Weed Detection

## Description
This project develops a Web-based Data Management Platform specifically designed for weed detection in sorghum fields. Utilizing advanced AI and high-resolution drone imagery, the platform provides farmers with a user-friendly interface to efficiently manage weed detection and analysis, promoting sustainable agricultural practices by reducing the dependency on chemical herbicides.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Installation
To set up this project, follow these steps:

1. Clone the repository and switch to the main branch:
   ```bash
   git clone https://github.com/ensarkaya/DataManagementPlatformForWeedDetection
   cd DataManagementPlatformForWeedDetection

2. Build and run the Docker containers:
    ```bash
    docker-compose up --build

3. Stop the Docker containers using `Ctrl + C`.

4. Open the `docker-compose.yml` file and modify the `osm-tile-server` image command from `import` to `run`.

5. Start the Docker containers again:
    ```bash
    docker-compose up 

## Usage
After installation, the platform can be accessed through a web interface. Users can register, log in, and start uploading drone-captured images of their fields for AI-powered weed analysis. The platform provides analysis on detected weeds, facilitating targeted herbicide application or mechanical removal.

## Contributing
Contributions to this project are welcome. You can contribute by:

1-Reporting bugs
2-Suggesting enhancements
3-Submitting pull requests with improvements

## License
This project is licensed under the MIT License - see the LICENSE file in the project repository for details.
