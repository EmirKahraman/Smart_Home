---

# Smart Home Energy Management

## Table of Contents
1. [Overview](#overview)
2. [Instructions](#instructions)
3. [Features](#features)
4. [Data Requirements](#data-requirements)
5. [Installation](#installation)
6. [Usage](#usage)
7. [Detailed Documentation](#detailed-documentation)
8. [Contributing](#contributing)
9. [License](#license)

## Overview
This project provides a smart home model designed to optimize power consumption. By managing energy loads and utilizing renewable energy sources, it helps analyze cost savings and improve energy efficiency.

## Instructions

1. Run the program.
2. Select a load profile and a meteorological data set.
3. Set the threshold value.
4. Press "Analyze".

The program will calculate:
- Cost savings with and without load shifting.
- Cost savings from PV panels (if installed).

## Features

- **Battery Management**
- **Solar Panel Integration**

## Data Requirements

- **Electric Load Profile**
- **Meteorological Data**

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/EmirKahraman/Smart_Home.git
   ```
2. Navigate to the project directory:
   ```bash
   cd Smart_Home
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Execute the main program:
```bash
python main.py
```


## Detailed Documentation
- [Report](./docs/reports.md)

## Contributing

Contributions are welcome! Please fork the repository and create a pull request.

## License

This project is licensed under the MIT License.

---