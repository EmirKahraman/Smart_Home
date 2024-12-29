import pandas as pd

class Battery:
    def _init_(self, capacity: float, charge_rate: float, discharge_rate: float, soc: float, panel_area: float, panel_efficiency: float):
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
            threshold (float): The threshold power level for peak hours.
            peak_hours (list): List of hours considered as peak hours.

        Returns:
            DataFrame: Modified profile with adjusted rated powers.
        """
        print(f"\nSimulating Battery...")
        discharge_log = []  # List to store discharge details per hour
        hourly_powers = self.calculate_hourly_power(profile_df)  # Calculate hourly power consumption

        for hour in range(24):
            irradiance = 0  
            if hour in solar_irradiance_df['Hour'].values:
                irradiance_row = solar_irradiance_df[solar_irradiance_df['Hour'] == hour]
                irradiance = irradiance_row.iloc[0]['Irradiation (kW/m^2)']

            print(f"Hour {hour} - Solar irradiance: {irradiance:.2f} kW/m^2, Current SoC: {self.soc:.2f}%")

            if self.soc < 80:
                if hour in peak_hours:
                    if self.soc < 50 and irradiance > 0:
                        self.charge_battery_with_solar(irradiance, in_peak_hours=True)
                else:
                    if irradiance > 0:
                        self.charge_battery_with_solar(irradiance, in_peak_hours=False)

            if hour in peak_hours:
                if self.soc < 30:
                    self.charge_battery_with_solar(irradiance, in_peak_hours=True)
                
                discharge_info = self.discharge_battery(hourly_powers[hour], threshold, hour)
                discharge_log.append(discharge_info)
            else:
                discharge_log.append({'Hour': hour, 'Discharge (kW)': 0, 'State of Charge (%)': self.soc})

        discharge_df = pd.DataFrame(discharge_log)
        print(f"\nDischarge Log:\n{discharge_df}")

        updated_df = self.update_profile(profile_df.copy(), discharge_df)
        
        print(f"Battery Simulation Complete.")
        return updated_df

    def discharge_battery(self, hourly_power, threshold, hour):
        """
        Attempt to discharge the battery during peak hours to reduce power consumption.

        Args:
            hourly_power (float): The power consumption for the current hour.
            threshold (float): The threshold for minimum power consumption.
            hour (int): The current hour being processed.

        Returns:
            dict: A dictionary containing discharge information for the hour.
        """
        if self.soc > 30 and hourly_power > threshold:
            print(f"Hour {hour} - Discharge conditions met. SoC is {self.soc}% and power needed is {hourly_power} kW (Threshold: {threshold} kW)")
            max_safe_discharge = (self.soc - 30) / 100 * self.capacity
            discharge = min(self.discharge_rate * self.capacity, hourly_power - threshold, max_safe_discharge)
            print(f"Hour {hour} - Calculated discharge: {discharge} kW")

            self.update_soc(-discharge * 100 / self.capacity)
            print(f"Hour {hour} - Updated SoC after discharge: {self.soc}%")
            return {'Hour': hour, 'Discharge (kW)': discharge, 'State of Charge (%)': self.soc}
        else:
            print(f"Hour {hour} - Discharge conditions not met: SoC = {self.soc}%, Power needed = {hourly_power} kW, Threshold = {threshold} kW")
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
            if in_peak_hours and self.soc < 50:
                charge_needed = (50 - self.soc) * self.capacity / 100.0
                charge = min(solar_power_kw, self.charge_rate * self.capacity, charge_needed)
            elif not in_peak_hours and self.soc < 80:
                charge_needed = (80 - self.soc) * self.capacity / 100.0
                charge = min(solar_power_kw, self.charge_rate * self.capacity, charge_needed)
            else:
                charge = 0
                
            self.update_soc((charge / self.capacity) * 100)

    def update_soc(self, change):
        """
        Update the State of Charge (SoC) of the battery.

        Args:
            change (float): The change in SoC percentage (positive for charging, negative for discharging).
        """
        self.soc = max(0, min(100, self.soc + change))

    @staticmethod
    def calculate_hourly_power(df):
        """
        Calculate the total power consumption for each hour.

        Args:
            df (DataFrame): The profile DataFrame containing appliance data.

        Returns:
            list: List of power consumption values for each hour.
        """
        hourly_power = [0] * 24
        
        for _, row in df.iterrows():
            start_time = int(row['Start'])
            end_time = int(row['End'])
            power = row['Rated Power (kW)']
            
            if start_time < end_time:
                for hour in range(start_time, end_time):
                    hourly_power[hour] += power
            else:
                for hour in range(start_time, 24):
                    hourly_power[hour] += power
                for hour in range(0, end_time):
                    hourly_power[hour] += power
        
        return hourly_power

    @staticmethod
    def update_profile(profile_df, discharge_df):
        """
        Updates the load profile by adding separate virtual appliances for battery discharge.

        Args:
            profile_df (DataFrame): DataFrame containing the load profile of appliances.
            discharge_df (DataFrame): DataFrame containing battery discharge data.

        Returns:
            DataFrame: Updated profile DataFrame including battery discharge entries.
        """
        print("\nUpdating profile with battery discharges...")

        new_rows = []
        for _, row in discharge_df.iterrows():
            hour = int(row["Hour"])
            discharge = row["Discharge (kW)"]

            if discharge > 0:
                battery_appliance_name = f"Battery Discharge (Hour {hour})"
                print(f"  Adding discharge: {battery_appliance_name} with {discharge:.3f} kW")

                new_rows.append({
                    "Name": battery_appliance_name,
                    "Rated Power (kW)": -discharge,  # Negative power to represent discharge
                    "Priority Group": 0,
                    "Start": hour,
                    "End": hour + 1
                })

        if new_rows:
            profile_df = pd.concat([profile_df, pd.DataFrame(new_rows)], ignore_index=True)

        return profile_df