---

# Smart Home Energy Management

## Table of Contents
1. [Introduction](#introduction)
2. [Instructions](#instructions)
3. [Data Requirements](#data-requirements)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Examples](#examples)
7. [License](#license)

## Introduction
This project provides a smart home model designed to optimize power consumption. By managing energy loads and utilizing renewable energy sources, it helps analyze cost savings and improve energy efficiency. Key features of this system include:
- **Battery Management:** Efficiently controls battery charge and discharge cycles to maximize energy usage and minimize costs.
- **Solar Panel Integration:** Incorporates photovoltaic (PV) panels into the energy system to leverage renewable energy sources.
- **Load Shifting:** Analyzes and adjusts energy loads to minimize peak demand and lower overall energy costs.

## Instructions

1. Run the program.
2. Select a load profile and a meteorological data set.
3. Set the threshold value.
4. Press "Analyze".

The program will calculate:
- Cost savings with and without load shifting.
- Cost savings from PV panels

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

## Examples
These values were calculated based on the load_profile_v3.xlsx and meteorological_data.csv

##### Solar Irradiation
<p align="center">
  <img src="./docs/solar.png" alt="Graph of solar irradiation data over a specific period"/>
  <br>
  <em>Figure 1: Graph of solar irradiation data over a specific period</em>
</p>

##### Battery Status
<p align="center">
  <img src="./docs/battery.png" alt="Graph showing the battery state of charge over time"/>
  <br>
  <em>Figure 2: Graph showing the battery state of charge over time</em>
</p>

#### Thresholds
Thresholds represent specific values set to analyze system behavior and outputs. The program calculates results and cost savings for the following threshold levels:

##### Threshold 3
<p align="center">
  <img src="./docs/tres3p.png" alt="Graph of system behavior for threshold level 3"/>
  <br>
  <em>Figure 3: Graph of system behavior for threshold level 3</em>
</p>

<p align="center">
  <img src="./docs/tres3c.png" alt="Bar chart showing cost savings for threshold level 3"/>
  <br>
  <em>Figure 4: Bar chart showing cost savings for threshold level 3</em>
</p>

##### Threshold 4
<p align="center">
  <img src="./docs/tres4p.png" alt="Graph of system behavior for threshold level 4"/>
  <br>
  <em>Figure 5: Graph of system behavior for threshold level 4</em>
</p>

<p align="center">
  <img src="./docs/tres4c.png" alt="Bar chart showing cost savings for threshold level 4"/>
  <br>
  <em>Figure 6: Bar chart showing cost savings for threshold level 4</em>
</p>

##### Threshold 5
<p align="center">
  <img src="./docs/tres5p.png" alt="Graph of system behavior for threshold level 5"/>
  <br>
  <em>Figure 7: Graph of system behavior for threshold level 5</em>
</p>

<p align="center">
  <img src="./docs/tres5c.png" alt="Bar chart showing cost savings for threshold level 5"/>
  <br>
  <em>Figure 8: Bar chart showing cost savings for threshold level 5</em>
</p>

##### Threshold 6
<p align="center">
  <img src="./docs/tres6p.png" alt="Graph of system behavior for threshold level 6"/>
  <br>
  <em>Figure 9: Graph of system behavior for threshold level 6</em>
</p>

<p align="center">
  <img src="./docs/tres6c.png" alt="Bar chart showing cost savings for threshold level 6"/>
  <br>
  <em>Figure 10: Bar chart showing cost savings for threshold level 6</em>
</p>

## License

This project is licensed under the MIT License.

---
