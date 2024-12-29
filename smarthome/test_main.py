import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

from modules.battery import Battery
from modules.load_profile import ElectricLoad
from modules.met_data import MeteorologicalData
from modules.calculations import Calculations

PEAK_START = 17
PEAK_END = 22

class EnergyAnalyzerApp:
    def _init_(self, root):
        self.root = root
        self.root.title("Energy Analyzer")
        self.threshold = tk.DoubleVar(value=3.0)

        # Universal default directory for file selection
        self.default_directory = os.path.abspath(os.path.join(os.path.dirname(_file_), 'data'))

        # File selection
        tk.Label(root, text="Select Load Profile File:").grid(row=0, column=0, padx=5, pady=5)
        tk.Button(root, text="Browse", command=self.select_load_file).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(root, text="Select Meteorological Data File:").grid(row=1, column=0, padx=5, pady=5)
        tk.Button(root, text="Browse", command=self.select_meteorology_file).grid(row=1, column=1, padx=5, pady=5)

        # Threshold input
        tk.Label(root, text="Set Threshold:").grid(row=2, column=0, padx=5, pady=5)
        tk.Entry(root, textvariable=self.threshold).grid(row=2, column=1, padx=5, pady=5)

        # Analyze button
        tk.Button(root, text="Analyze", command=self.run_analysis).grid(row=3, column=0, columnspan=2, pady=10)

        # Output area
        self.output_text = tk.Text(root, wrap=tk.WORD, height=15, width=50)
        self.output_text.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # Initialize file paths as None
        self.load_file_path = None
        self.met_file_path = None

    def select_load_file(self):
        self.load_file_path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx")],
            initialdir=self.default_directory
        )
        if self.load_file_path:
            try:
                print(f"Load profile file selected: {self.load_file_path}")
                self.default_load_dir = os.path.dirname(self.load_file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Error loading file: {str(e)}")

    def select_meteorology_file(self):
        self.met_file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")],
            initialdir=self.default_directory
        )
        if self.met_file_path:
            try:
                print(f"Meteorological data file selected: {self.met_file_path}")
                self.default_met_dir = os.path.dirname(self.met_file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Error loading file: {str(e)}")

    def run_analysis(self):
        if not self.load_file_path or not self.met_file_path:
            messagebox.showerror("Error", "Please select both load profile and meteorological data files.")
            return
        
        try:                            
            # Load data
            winter_profile_df, summer_profile_df = ElectricLoad.from_excel(self.load_file_path)
            winter_meteorological_df, summer_meteorological_df = MeteorologicalData.from_csv(self.met_file_path)
            
            threshold = self.threshold.get()
            temp = self.generate_hourly_profile(winter_profile_df)
            max_rated_power = max(temp['Power (kW)'])
            peak_hours = list(range(PEAK_START, PEAK_END + 1))

            # Winter analysis
            battery = Battery(
                capacity=max_rated_power * 0.5,
                charge_rate=0.2,
                discharge_rate=0.3,
                soc=(max_rated_power * 0.5) * 0.1,
                panel_area=10,
                panel_efficiency=.70,
            )

            battery_winter_profile_df = battery.simulate_battery(winter_profile_df, winter_meteorological_df, threshold, peak_hours)
            shifted_winter_profile_df = Calculations.shift_loads(battery_winter_profile_df, threshold, peak_hours)

            winter_cost = Calculations.calculate_energy_cost(winter_profile_df, peak_hours)
            battery_winter_cost = Calculations.calculate_energy_cost(battery_winter_profile_df, peak_hours)
            shifted_winter_cost = Calculations.calculate_energy_cost(shifted_winter_profile_df, peak_hours)

            # Summer analysis
            battery = Battery(
                capacity=max_rated_power * 0.5,
                charge_rate=0.2,
                discharge_rate=0.3,
                soc=0.1 * max_rated_power * 0.5,
                panel_area=10,
                panel_efficiency=.70,
            )

            battery_summer_profile_df = battery.simulate_battery(summer_profile_df, summer_meteorological_df, threshold, peak_hours)
            shifted_summer_profile_df = Calculations.shift_loads(battery_summer_profile_df, threshold, peak_hours)

            summer_cost = Calculations.calculate_energy_cost(summer_profile_df, peak_hours)
            battery_summer_cost = Calculations.calculate_energy_cost(battery_summer_profile_df, peak_hours)
            shifted_summer_cost = Calculations.calculate_energy_cost(shifted_summer_profile_df, peak_hours)

            # Display results in the output text box
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, f"Winter Hourly Energy Cost (Original): {winter_cost:.3f} $\n")
            self.output_text.insert(tk.END, f"Winter Hourly Energy Cost (Battery): {battery_winter_cost:.3f} $\n")
            self.output_text.insert(tk.END, f"Winter Hourly Energy Cost (Shifted): {shifted_winter_cost:.3f} $\n")

            self.output_text.insert(tk.END, f"\nSummer Hourly Energy Cost (Original): {summer_cost:.3f} $\n")
            self.output_text.insert(tk.END, f"Summer Hourly Energy Cost (Battery): {battery_summer_cost:.3f} $\n")
            self.output_text.insert(tk.END, f"Summer Hourly Energy Cost (Shifted): {shifted_summer_cost:.3f} $\n")

            # Plot the profiles
            self.plot_seasonal_profiles(
                winter_profile_df, battery_winter_profile_df, shifted_winter_profile_df,
                summer_profile_df, battery_summer_profile_df, shifted_summer_profile_df
            )
        
        except Exception as e:
            messagebox.showerror("Error", str(e))

    @staticmethod
    def plot_seasonal_profiles(winter_df, battery_winter_df, shifted_winter_df, summer_df, battery_summer_df, shifted_summer_df):
        """Plot winter and summer profiles as bar charts."""
        
        # Generate hourly profiles
        winter_hourly = EnergyAnalyzerApp.generate_hourly_profile(winter_df)
        battery_winter_hourly = EnergyAnalyzerApp.generate_battery_profile(winter_df, battery_winter_df)
        shifted_winter_hourly = EnergyAnalyzerApp.generate_hourly_profile(shifted_winter_df)
        
        summer_hourly = EnergyAnalyzerApp.generate_hourly_profile(summer_df)
        battery_summer_hourly = EnergyAnalyzerApp.generate_battery_profile(summer_df, battery_summer_df)
        shifted_summer_hourly = EnergyAnalyzerApp.generate_hourly_profile(shifted_summer_df)

        # Create subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        
        # Bar width and positions
        width = 0.25
        x = np.arange(24)
        
        # Winter plot
        ax1.bar(x - width, winter_hourly['Power (kW)'], width, label='Original Profile', color='blue', alpha=0.7)
        ax1.bar(x, battery_winter_hourly['Power (kW)'], width, label='Battery Profile', color='green', alpha=0.7)
        ax1.bar(x + width, shifted_winter_hourly['Power (kW)'], width, label='Shifted Profile', color='red', alpha=0.7)
        ax1.set_title('Winter Load Profiles')
        ax1.set_xlabel('Hour of Day')
        ax1.set_ylabel('Power (kW)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Summer plot
        ax2.bar(x - width, summer_hourly['Power (kW)'], width, label='Original Profile', color='blue', alpha=0.7)
        ax2.bar(x, battery_summer_hourly['Power (kW)'], width, label='Battery Profile', color='green', alpha=0.7)
        ax2.bar(x + width, shifted_summer_hourly['Power (kW)'], width, label='Shifted Profile', color='red', alpha=0.7)
        ax2.set_title('Summer Load Profiles')
        ax2.set_xlabel('Hour of Day')
        ax2.set_ylabel('Power (kW)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    @staticmethod
    def generate_battery_profile(original_df, battery_df):
        """Generate the actual battery profile by subtracting battery discharge from original profile."""
        
        # Get the original hourly profile
        hourly_profile = EnergyAnalyzerApp.generate_hourly_profile(original_df)
        
        # Extract battery discharge entries
        battery_entries = battery_df[battery_df['Name'].str.contains('Battery Discharge', na=False)]
        
        # Create battery discharge profile
        battery_discharge = pd.DataFrame(0, index=np.arange(24), columns=['Power (kW)'])
        
        # Sum up battery discharge for each hour
        for _, row in battery_entries.iterrows():
            hour = int(row['Start'])
            discharge = abs(row['Rated Power (kW)'])  # Convert negative discharge to positive
            battery_discharge.loc[hour, 'Power (kW)'] += discharge
        
        # Subtract battery discharge from original profile
        battery_profile = hourly_profile.copy()
        battery_profile['Power (kW)'] -= battery_discharge['Power (kW)']
        
        return battery_profile

    @staticmethod
    def generate_hourly_profile(df):
        # Create an empty DataFrame to store hourly data
        hourly_profile = pd.DataFrame(0, index=np.arange(24), columns=['Power (kW)'])
        
        # Iterate through each row (appliance data)
        for _, row in df.iterrows():
            start_time = row['Start']
            end_time = row['End']
            power = row['Rated Power (kW)']
            
            # If start and end times are within the same day
            if start_time < end_time:
                # Add the power to the corresponding hours
                hourly_profile.loc[int(start_time):int(end_time)-1, 'Power (kW)'] += power
            # If the times span over midnight
            else:
                hourly_profile.loc[int(start_time):23, 'Power (kW)'] += power
                hourly_profile.loc[0:int(end_time)-1, 'Power (kW)'] += power
        
        return hourly_profile