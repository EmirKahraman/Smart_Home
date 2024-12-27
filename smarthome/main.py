import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt

import os   # For path

from modules.battery import Battery
from modules.load_profile import ElectricLoad
from modules.met_data import MeteorologicalData
from modules.calculations import Calculations

PEAK_START = 17
PEAK_END = 22


class EnergyAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Energy Analyzer")
        self.threshold = tk.DoubleVar(value=3.0)

        # Universal default directory for file selection
        self.default_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

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
        # Open file dialog for selecting the load profile file
        self.load_file_path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx")],
            initialdir=self.default_directory  # Set universal default directory
        )
        if self.load_file_path:
            try:
                # Validate file format or load preview here
                print(f"Load profile file selected: {self.load_file_path}")
                self.default_load_dir = os.path.dirname(self.load_file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Error loading file: {str(e)}")

    def select_meteorology_file(self):
        # Open file dialog for selecting the meteorological data file
        self.met_file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")],
            initialdir=self.default_directory  # Set universal default directory
        )
        if self.met_file_path:
            try:
                # Validate file format or load preview here
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
            print("\nLoading data...")
            winter_profile_df, summer_profile_df = ElectricLoad.from_excel(self.load_file_path)
            winter_meteorological_df, summer_meteorological_df = MeteorologicalData.from_csv(self.met_file_path)
            
            threshold = self.threshold.get()                    # Get the threshold value
            print(f"Threshold set to: {threshold}")
            max_row = winter_profile_df.loc[winter_profile_df['Rated Power (kW)'].idxmax()]
            max_rated_power = max_row['Rated Power (kW)']
            print(f"Max load set to: {max_rated_power}")
            peak_hours = list(range(PEAK_START, PEAK_END + 1))  # Define peak hours
            print(f"Peak hours: {peak_hours}")

            # Create a battery instance for winter
            battery = Battery(      # Create a battery instance
                capacity=max_rated_power * 0.5,  # 50% of max rated power as capacity
                charge_rate=0.2,    # Charge rate set to 0.2 kW
                discharge_rate=0.3,     # Discharge rate set to 0.3 kW
                soc=0.1 * max_rated_power * 0.5,  # Initial SoC set to 10% of capacity
                panel_area=10,
                panel_efficiency=.70,
            )

            battery_discharge_profile_winter = battery.simulate_battery(winter_profile_df, winter_meteorological_df, threshold, peak_hours)    # Manage battery for winter profile
            shifted_winter_profile_df = Calculations.load_shifting(winter_profile_df, battery_discharge_profile_winter, threshold, peak_hours)    # Shift winter profile

            winter_cost = Calculations.calculate_energy_cost(winter_profile_df, peak_hours)
            shifted_winter_cost = Calculations.calculate_energy_cost(shifted_winter_profile_df, peak_hours)    

            # Create a battery instance for summer
            battery = Battery(      # Create a battery instance
                capacity=max_rated_power * 0.5,  # 50% of max rated power as capacity
                charge_rate=0.2,    # Charge rate set to 0.2 kW
                discharge_rate=0.3,     # Discharge rate set to 0.3 kW
                soc=0.1 * max_rated_power * 0.5,  # Initial SoC set to 10% of capacity
                panel_area=10,
                panel_efficiency=.70,
            )

            battery_discharge_profile_summer = battery.simulate_battery(summer_profile_df, summer_meteorological_df, threshold, peak_hours)    # Manage battery for summer profile
            shifted_summer_profile_df = Calculations.load_shifting(summer_profile_df, battery_discharge_profile_summer, threshold, peak_hours)    # Shift summer profile

            summer_cost = Calculations.calculate_energy_cost(summer_profile_df, peak_hours)
            shifted_summer_cost = Calculations.calculate_energy_cost(shifted_summer_profile_df, peak_hours)
            
            # Output the results
            print(f"\nWinter energy cost: {winter_cost}")
            print(f"Shifted winter energy cost: {shifted_winter_cost}")
            print(f"Summer energy cost: {summer_cost}")
            print(f"Shifted summer energy cost: {shifted_summer_cost}")

            # Display results in the output text box
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, f"Winter Hourly Energy Cost (Original): {winter_cost:.3f} $\n")
            self.output_text.insert(tk.END, f"Winter Hourly Energy Cost (Shifted): {shifted_winter_cost:.3f} $\n")
            self.output_text.insert(tk.END, f"Summer Hourly Energy Cost (Original): {summer_cost:.3f} $\n")
            self.output_text.insert(tk.END, f"Summer Hourly Energy Cost (Shifted): {shifted_summer_cost:.3f} $\n")
            
            # Plot results
            self.plot_load_profile(winter_profile_df, shifted_winter_profile_df, peak_hours)            
            self.plot_load_profile_alternative(winter_profile_df, shifted_winter_profile_df)
            self.plot_load_profile(summer_profile_df, shifted_summer_profile_df, peak_hours)
            self.plot_load_profile_alternative(summer_profile_df, shifted_summer_profile_df)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    @staticmethod
    def plot_load_profile(original_profile, shifted_profile, peak_hours):
        print("\nPlotting graphs...")
        plt.figure(figsize=(12, 6))

        hours = range(24)

        bar_width = 0.35
        print("Orginal")
        plt.bar(hours, original_profile, bar_width, label='Original Profile', color='blue', alpha=0.6)
        #### PLOT BATTERY as well
        print("Shifted")
        plt.bar([x + bar_width for x in hours], shifted_profile, bar_width, label='Shifted Profile', color='red', alpha=0.6)
        
        plt.axvspan(min(peak_hours)-0.5, max(peak_hours)+0.5, color='yellow', alpha=0.2, label='Peak Hours')
        
        plt.xlabel('Hour of Day')
        plt.ylabel('Power (kW)')
        plt.title('Load Profile Comparison')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    @staticmethod
    def plot_load_profile_alternative(original_profile, shifted_profile):
        plt.figure(figsize=(12, 8))

        plt.subplot(2, 1, 1)
        plt.plot(original_profile, label="Original Winter", color="blue")
        plt.plot(shifted_profile, label="Shifted Winter", color="cyan", linestyle="--")
        plt.title("Winter Profiles")
        plt.xlabel("Hour of the Day")
        plt.ylabel("Energy (kW)")
        plt.legend()
        plt.grid()

        plt.tight_layout()
        plt.show()


# Run the GUI application
if __name__ == "__main__":
    root = tk.Tk()
    app = EnergyAnalyzerApp(root)
    root.mainloop()