---

# Smart Home Energy Management

## Table of Contents
1. [Introduction](#introduction)
2. [Instructions](#instructions)
3. [Features](#features)
4. [Data Requirements](#data-requirements)
5. [Installation](#installation)
6. [Setup](#setup)
7. [Usage](#usage)
8. [Examples](#examples)
9. [License](#license)

## Introduction
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
- **Load Shifting**

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

## Setup
1. Set up environment variables if required.
2. Ensure all dependencies are installed.

## Usage

Execute the main program:
```bash
python main.py
```

## Examples
These values were calculated based on the load_profile_v3.xlsx and meteorological_data.csv

#### Solar Irradiation
<p align="center">
  <img src="./docs/solar.png" alt="Electric Load Profile Data"/>
  <br>
  <em>Figure 1: Solar Irradiation Data</em>
</p>

#### Battery Status
<p align="center">
  <img src="./docs/battery.png" alt="Meteorological Data"/>
  <br>
  <em>Figure 2: Battery Status</em>
</p>

#### Threshold 3
<p align="center">
  <img src="./docs/tres3p.png" alt="Results for Threshold 3"/>
  <br>
  <em>Figure 3: Results for Threshold 3</em>
</p>

<p align="center">
  <img src="./docs/tres3c.png" alt="Cost Savings for Threshold 3"/>
  <br>
  <em>Figure 4: Cost Savings for Threshold 3</em>
</p>

#### Threshold 4
<p align="center">
  <img src="./docs/tres4p.png" alt="Results for Threshold 4"/>
  <br>
  <em>Figure 5: Results for Threshold 4</em>
</p>

<p align="center">
  <img src="./docs/tres4c.png" alt="Cost Savings for Threshold 4"/>
  <br>
  <em>Figure 6: Cost Savings for Threshold 4</em>
</p>

#### Threshold 5
<p align="center">
  <img src="./docs/tres5p.png" alt="Results for Threshold 5"/>
  <br>
  <em>Figure 7: Results for Threshold 5</em>
</p>

<p align="center">
  <img src="./docs/tres5c.png" alt="Cost Savings for Threshold 5"/>
  <br>
  <em>Figure 8: Cost Savings for Threshold 5</em>
</p>

#### Threshold 6
<p align="center">
  <img src="./docs/tres6p.png" alt="Results for Threshold 6"/>
  <br>
  <em>Figure 9: Results for Threshold 6</em>
</p>

<p align="center">
  <img src="./docs/tres6c.png" alt="Cost Savings for Threshold 6"/>
  <br>
  <em>Figure 10: Cost Savings for Threshold 6</em>
</p>

## License

This project is licensed under the MIT License.

---
