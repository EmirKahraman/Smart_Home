import pandas as pd

class Battery:
    def __init__(self, capacity: float, charge_rate: float, discharge_rate: float, soc: float, panel_area: float, panel_efficiency: float):
        self.capacity = capacity  # kWh
        self.charge_rate = charge_rate  # kW
        self.discharge_rate = discharge_rate  # kW
        self.soc = soc  # State of charge (%)
        self.panel_area = panel_area  # m^2
        self.panel_efficiency = panel_efficiency  # Efficiency (decimal)

    def simulate_battery(self, profile_df, solar_irradiance_df, threshold, peak_hours):
        """
        Simulate the battery operation, adjusting the device consumption based on the available solar power and battery SoC.

        Args:
            profile_df (DataFrame): Hourly energy consumption profile (kW).
            solar_irradiance_df (DataFrame): Hourly solar irradiance values (kW/m^2).
            peak_hours (list): List of hours considered as peak hours.

        Returns:
            DataFrame: Modified profile with adjusted rated powers.
        """
        print(f"\nSimulating Battery...")
        discharge_log = []  # List to store discharge details per hour

        for hour in range(24):
            irradiance = 0  
            if hour in solar_irradiance_df['Hour'].values:  # Get solar irradiance for the current hour
                irradiance_row = solar_irradiance_df[solar_irradiance_df['Hour'] == hour]
                irradiance = irradiance_row.iloc[0]['Irradiation (kW/m^2)']

            print(f"Hour {hour} - Solar irradiance: {irradiance:.2f} kW/m^2, Current SoC: {self.soc:.2f}%")

            if self.soc < 80:   # Charge battery with solar energy if SoC is below 80%
                if hour in peak_hours:
                    # In peak hours, charge up to 50% if solar irradiance is available
                    if self.soc < 50 and irradiance > 0:
                        self.charge_battery_with_solar(irradiance, in_peak_hours=True)
                else:
                    if irradiance > 0:
                        self.charge_battery_with_solar(irradiance, in_peak_hours=False)

            if hour in peak_hours:  # Discharge logic during peak hours
                if self.soc < 30:  # Recharge if SoC is below 30% in peak hours
                    self.charge_battery_with_solar(irradiance, in_peak_hours=True)
                
                discharge_info = self.discharge_battery(profile_df, threshold, hour)
                discharge_log.append(discharge_info)

        discharge_df = pd.DataFrame(discharge_log)  # Combine all discharge information into a single DataFrame
        print(f"\n{discharge_df}")
        return discharge_df

    def discharge_battery(self, profile_df, threshold, hour):
        """
        Attempt to discharge the battery during peak hours to reduce appliance power consumption.

        Args:
            profile_df (DataFrame): The profile DataFrame containing appliance data.
            threshold (float): The threshold for minimum power consumption.
            hour (int): The current hour being processed.

        Returns:
            dict: A dictionary containing discharge information for the hour.
        """
        total_power_needed = profile_df['Rated Power (kW)'].sum()

        if self.soc > 30 and total_power_needed > threshold:    # Check if discharge conditions are met
            print(f"Hour {hour} - Discharge conditions met. SoC is {self.soc}% and total power needed is {total_power_needed} kW (Threshold: {threshold} kW)")
            max_safe_discharge = (self.soc - 30) / 100 * self.capacity
            discharge = min(self.discharge_rate * self.capacity, total_power_needed - threshold, max_safe_discharge)
            print(f"Hour {hour} - Calculated discharge: {discharge} kW")

            self.update_soc(-discharge * 100 / self.capacity)   # Update State of Charge (SoC)
            print(f"Hour {hour} - Updated SoC after discharge: {self.soc}%")
            return {'Hour': hour, 'Discharge (kW)': discharge, 'State of Charge (%)': self.soc}
        else:
            print(f"Hour {hour} - Discharge conditions not met: SoC = {self.soc}%, Total power needed = {total_power_needed} kW, Threshold = {threshold} kW")
            return {'Hour': hour, 'Discharge (kW)': 0, 'State of Charge (%)': self.soc}

    def charge_battery_with_solar(self, irradiance, in_peak_hours=False):
        """
        Charges the battery with solar energy, ensuring it does not exceed the SoC limits.

        Args:
            irradiance (float): Solar irradiance for the specific hour (kW/m^2).
            in_peak_hours (bool): Whether the charging is occurring during peak hours.
        """
        if irradiance > 0:
            solar_power_kw = irradiance * self.panel_area * self.panel_efficiency
            if in_peak_hours and self.soc < 50:  # Charge to 50% in peak hours
                charge_needed = (50 - self.soc) * self.capacity / 100.0
                charge = min(solar_power_kw, self.charge_rate * self.capacity, charge_needed)
            elif not in_peak_hours and self.soc < 80:  # Charge to 80% in non-peak hours
                charge_needed = (80 - self.soc) * self.capacity / 100.0
                charge = min(solar_power_kw, self.charge_rate * self.capacity, charge_needed)
            else:
                charge = 0
                
            self.update_soc((charge / self.capacity) * 100)  # Update SoC with charged energy percentage

    def update_soc(self, change):
        """
        Update the State of Charge (SoC) of the battery.

        Args:
            change (float): The change in SoC percentage (positive for charging, negative for discharging).
        """
        self.soc = max(0, min(100, self.soc + change))  # Ensure SoC stays between 0% and 100%
