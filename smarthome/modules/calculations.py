"""
This module provides utility methods for managing and optimizing energy usage 
in a load profile system for residential or commercial settings. It includes 
functions to update the load profile based on battery discharge, shift loads 
from peak to off-peak hours to reduce energy costs, and calculate total energy 
costs based on different tariff rates for peak, mid-peak, and off-peak periods.

Classes:
    - Calculations: A class containing static methods for updating load profiles,
      shifting loads, and calculating energy costs.
Methods:
    - update_profile(profile_df, battery_discharge_profile): Updates the load profile
    - shift_loads(profile_df, threshold, peak_hours): Shifts loads within peak hours
    - calculate_energy_cost(profile_df, peak_hours): Calculates the energy cost

Constants:
    - PEAK_START: The start hour for peak pricing (17:00).
    - PEAK_END: The end hour for peak pricing (22:00).
    - OFF_PEAK_TARIFF: The tariff rate for off-peak hours.
    - MID_PEAK_TARIFF: The tariff rate for mid-peak hours (6:00 - 17:00).
    - PEAK_TARIFF: The tariff rate for peak hours (17:00 - 22:00).
"""

import pandas as pd

PEAK_START = 17
PEAK_END = 22

OFF_PEAK_TARIFF = 0.1
MID_PEAK_TARIFF = 0.2
PEAK_TARIFF = 0.3

class Calculations:

    @staticmethod
    def update_profile(profile_df, battery_discharge_profile):
        """
        Updates the load profile by subtracting battery discharge for each active hour,
        modifying the input DataFrame.

        Parameters:
        - profile_df: DataFrame containing the load profile of appliances.
        - battery_discharge_profile: DataFrame containing battery discharge data (hour and discharge power).

        Returns:
        - Updated profile DataFrame with the battery discharge applied.
        """
        print("\nUpdating profile with battery discharge...")

        # Iterate over each row in the battery discharge profile
        for _, row in battery_discharge_profile.iterrows():
            hour = int(row["Hour"])  # Extract the hour (assuming it is an integer)
            discharge = row["Discharge (kW)"]  # Extract the discharge value

            # If no discharge (battery is empty or no discharge), skip this hour
            if discharge <= 0:
                print(f"  Hour {hour}: Battery is empty or no discharge, no adjustment applied.")
                continue  # Skip if no discharge (battery is empty or has no discharge)
            
            print(f"  Hour {hour}: Battery Discharge = {discharge:.3f} kW")

            # Iterate through appliances to apply the discharge to running appliances
            for index, appliance in profile_df.iterrows():
                appliance_name = appliance["Name"]
                start = appliance["Start"]
                end = appliance["End"]
                rated_power = appliance["Rated Power (kW)"]

                # Check if the appliance is active during this hour (handles overnight appliances)
                if start <= hour < end or (start > end and (hour >= start or hour < end)):
                    original_load = rated_power
                    # Apply discharge to the appliance load, if it is running during this hour
                    updated_load = max(0, original_load - discharge)  # Ensure load does not go below 0
                    profile_df.at[index, "Rated Power (kW)"] = updated_load
                    print(f"    Appliance: {appliance_name}")
                    print(f"      Original Load: {original_load:.3f} kW, Updated Load: {updated_load:.3f} kW")
                else:
                    print(f"    Appliance: {appliance_name} not running at hour {hour}, no change.")

        print("Profile update completed.")
        return profile_df
    
    @staticmethod
    def shift_loads(profile_df, threshold, peak_hours):
        """
        Shifts loads within peak hours (17:00 to 22:00) to off-peak hours to reduce energy costs,
        starting with the highest-priority loads and stopping once errors are satisfied.
        
        Parameters:
        - profile_df: DataFrame containing the load profile of appliances.
        - threshold: Maximum allowable load in any hour to prevent overloading the grid.
        - peak_hours: List of hours considered as peak hours.

        Returns:
        - Updated profile DataFrame with adjusted load timings.
        """
        print("\nShifting loads to reduce threshold violations...")

        # Initialize a dictionary to track the summed load for each peak hour
        peak_hour_loads = {hour: 0 for hour in peak_hours}

        # Calculate the total load for each peak hour, including overnight schedules
        for _, row in profile_df.iterrows():
            start, end = row["Start"], row["End"]
            rated_power = row["Rated Power (kW)"]

            if rated_power == 0:
                continue

            # Adjust for overnight schedules
            hours_to_consider = list(range(int(start), int(end))) if end > start else list(range(int(start), 24)) + list(range(0, int(end)))
            for hour in hours_to_consider:
                if hour in peak_hours:
                    peak_hour_loads[hour] += rated_power

        # Calculate errors for each peak hour
        errors = {hour: max(0, peak_hour_loads[hour] - threshold) for hour in peak_hours}
        print(f"Initial peak hour load errors: {errors}")

        # Sort appliances by their priority group (highest priority first)
        sorted_profile = profile_df.sort_values(by="Priority Group", ascending=False)

        # Process each load to shift it out of peak hours and reduce error
        for index, row in sorted_profile.iterrows():
            name = row["Name"]
            start, end = row["Start"], row["End"]
            rated_power = row["Rated Power (kW)"]
            priority = row["Priority Group"]

            if rated_power == 0:
                continue  # Skip zero-power loads

            print(f"Processing load: {name} ({rated_power} kW) with priority {priority}")
            print(f"  Original schedule: Start = {start}, End = {end}")

            # Check if load overlaps with peak hours
            overlaps = any(hour in peak_hours for hour in range(int(start), int(end))) if end > start else \
                    any(hour in peak_hours for hour in list(range(int(start), 24)) + list(range(0, int(end))))

            if not overlaps:
                continue

            # Attempt to shift the load to reduce the highest error
            for hour in peak_hours:
                if errors[hour] == 0:
                    continue  # Skip hours where error is already resolved

                # Attempt to shift the load to a non-peak hour after 22:00
                shift_start = 23  # Example shift hour, adjust as needed
                shift_end = (shift_start + (int(end) - int(start))) % 24
                shift_hours = list(range(shift_start, shift_end)) if shift_end > shift_start else \
                            list(range(shift_start, 24)) + list(range(0, shift_end))

                valid_shift = all(peak_hour_loads.get(h, 0) + rated_power <= threshold for h in shift_hours)

                if valid_shift:
                    print(f"  Shifting load to start at hour {shift_start}")

                    # Update the profile with the new start and end times
                    profile_df.at[index, "Start"] = int(shift_start)  # Cast to int
                    profile_df.at[index, "End"] = int(shift_end)  # Cast to int

                    # Update peak_hour_loads and errors incrementally
                    original_hours = list(range(int(start), int(end))) if end > start else list(range(int(start), 24)) + list(range(0, int(end)))
                    for hour in original_hours:
                        if hour in peak_hours:
                            peak_hour_loads[hour] -= rated_power
                            errors[hour] = max(0, peak_hour_loads[hour] - threshold)

                    for hour in shift_hours:
                        if hour in peak_hours:
                            peak_hour_loads[hour] += rated_power
                            errors[hour] = max(0, peak_hour_loads[hour] - threshold)

                    break  # Move to the next load after a successful shift

                # Stop processing this hour if the error is fully resolved
                if errors[hour] == 0:
                    print(f"Error for hour {hour} is resolved.")
                    break

        print(f"\nUpdated Load Profile:\n{profile_df}")
        print("Load shifting completed.")
        return profile_df
        
    @staticmethod
    def calculate_energy_cost(profile_df, peak_hours):
        """
        Calculate the energy cost based on consumption during peak, mid-peak, and off-peak hours.
        
        Parameters:
        - profile_df: DataFrame containing the hourly load profile of appliances.
        - peak_hours: List of hours considered peak hours (e.g., 17:00 to 22:00).
        
        Returns:
        - Total energy cost calculated based on consumption during peak, mid-peak, and off-peak hours.
        """
        print(f"\nCalculating energy cost...")

        # Initialize hourly consumption profile with zeros for each hour of the day
        hourly_profile_df = {hour: 0 for hour in range(24)}

        # Update the hourly consumption profile based on each appliance's usage time
        for _, device in profile_df.iterrows():
            start = int(device['Start']) if not pd.isna(device['Start']) else 0
            end = int(device['End']) if not pd.isna(device['End']) else 24

            # If end time is before start time, assume the appliance runs overnight
            if end < start:
                end += 24  # adjust the end time to account for overnight use

            # Update the profile for each device from start to end hour
            for hour in range(start, min(end, 24)):
                hourly_profile_df[hour] += device['Rated Power (kW)']
            # Handle wrap-around for appliances running past midnight (e.g., 23:00 - 2:00)
            if end > 24:
                for hour in range(0, end % 24):
                    hourly_profile_df[hour] += device['Rated Power (kW)']

        # Print the hourly consumption profile for debugging
        print("Hourly Consumption Profile:")
        print(hourly_profile_df)

        # Initialize the total cost
        total_cost = 0

        # Loop through each hour to calculate the cost based on the tariff
        for hour in range(24):
            consumption = hourly_profile_df[hour]
            if hour in peak_hours:
                cost = consumption * PEAK_TARIFF
                print(f"Hour {hour}: Peak rate {PEAK_TARIFF} -> Cost: {round(cost, 2)}")
                total_cost += cost
            elif 6 <= hour < 17:
                cost = consumption * MID_PEAK_TARIFF
                print(f"Hour {hour}: Mid-peak rate {MID_PEAK_TARIFF} -> Cost: {round(cost, 2)}")
                total_cost += cost
            else:
                cost = consumption * OFF_PEAK_TARIFF
                print(f"Hour {hour}: Off-peak rate {OFF_PEAK_TARIFF} -> Cost: {round(cost, 2)}")
                total_cost += cost

        # Round total cost for better readability
        total_cost = round(total_cost, 2)
        print(f"\nTotal Energy Cost: {total_cost}")

        print("Energy cost calculation completed.")
        return total_cost