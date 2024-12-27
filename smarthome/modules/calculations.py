import pandas as pd

PEAK_START = 17
PEAK_END = 22

OFF_PEAK_TARIFF = 0.1
MID_PEAK_TARIFF = 0.2
PEAK_TARIFF = 0.3

#### ROUND VALUES BY .3f 
class Calculations:
    @staticmethod
    #### THİS WONT WORK
    #### kaydırılmıs profil profile df gibi bir veri göndermeli saatleri değişmiş olarak
    def load_shifting(profile_df, discharge_df, threshold, peak_hours):
        # Create initial hourly profile from discharge data
        hourly_profile = {hour: 0 for hour in range(24)}
        for _, row in discharge_df.iterrows():
            hour = int(row['Hour'])
            hourly_profile[hour] += row['Discharge (kW)']
        
        shifted_profile = pd.Series(hourly_profile)
        print("\nInitial Hourly Profile:")
        print(shifted_profile)
            
        # Adjust loads from profile_df
        for _, load in profile_df.iterrows():
            load_power = load['Rated Power (kW)']
            print(f"\nAttempting to shift load of {load_power} kW")
            
            for hour in peak_hours:
                if shifted_profile[hour] > threshold:
                    for new_hour in range(24):
                        if new_hour not in peak_hours:
                            print(f"  Load at peak hour {hour} exceeds threshold ({shifted_profile[hour]} > {threshold}).")

                            if shifted_profile[new_hour] + load_power <= threshold:
                                print(f"    Shifting load to hour {new_hour}.")
                                shifted_profile[hour] -= load_power
                                shifted_profile[new_hour] += load_power
                                break
        print("\nShifted Hourly Profile:")
        print(shifted_profile)
          
        return shifted_profile
    
    @staticmethod
    #### TAKE A LOK AT THİS COST TOO LOW
    def calculate_energy_cost(profile_df, peak_hours):
        print(f"\nCalculating energy cost...")

        cost = 0
        
        if isinstance(profile_df, pd.Series):
            profile_df = profile_df.to_dict()
        elif isinstance(profile_df, pd.DataFrame):
            hourly_profile_df = {hour: 0 for hour in range(24)}
            for _, device in profile_df.iterrows():
                start = int(device['Start']) if not pd.isna(device['Start']) else 0
                end = int(device['End']) if not pd.isna(device['End']) else 24
                if end > start:
                    for hour in range(start, min(end, 24)):
                        hourly_profile_df[hour] += device['Rated Power (kW)']
            profile_df = hourly_profile_df

        print("Hourly Consumption Profile:")
        print(profile_df)

        for hour in range(24):
            consumption = float(profile_df.get(hour, 0))
            
            if hour in peak_hours:
                cost += consumption * PEAK_TARIFF
                print(f"Hour {hour}: Peak rate {PEAK_TARIFF} -> Cost: {consumption * PEAK_TARIFF}")
            elif 6 <= hour < 17:
                cost += consumption * MID_PEAK_TARIFF
                print(f"Hour {hour}: Mid-peak rate {MID_PEAK_TARIFF} -> Cost: {consumption * MID_PEAK_TARIFF}")
            else:
                cost += consumption * OFF_PEAK_TARIFF
                print(f"Hour {hour}: Off-peak rate {OFF_PEAK_TARIFF} -> Cost: {consumption * OFF_PEAK_TARIFF}")
        
        print(f"\nTotal Energy Cost: {cost}")

        return cost