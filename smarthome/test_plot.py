staticmethod
    def plot_seasonal_profiles(winter_hourly, battery_winter_hourly, shifted_winter_hourly, winter_meteorological_df, 
                            summer_hourly, battery_summer_hourly, shifted_summer_hourly, summer_meteorological_df, peak_hours):
        """Plot winter and summer profiles as bar charts."""
        
        # Create subplots for load profiles
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        
        # Bar width ve positions
        width = 0.35
        x = np.arange(24)
        
        # Winter plot
        ax1.bar(x - width/2, winter_hourly['Power (kW)'], width, label='Original Profile', color='blue', alpha=0.7)
        ax1.bar(x + width/2, shifted_winter_hourly['Power (kW)'], width, label='Shifted Profile', color='red', alpha=0.7)
        ax1.axvspan(min(peak_hours)-0.5, max(peak_hours)+0.5, color='yellow', alpha=0.2, label='Peak Hours')
        ax1.set_title('Winter Load Profiles')
        ax1.set_xlabel('Hour of Day')
        ax1.set_ylabel('Power (kW)')
        ax1.set_xticks(x)
        ax1.set_xticklabels([str(i) for i in range(24)])
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Summer plot
        ax2.bar(x - width/2, summer_hourly['Power (kW)'], width, label='Original Profile', color='blue', alpha=0.7)
        ax2.bar(x + width/2, shifted_summer_hourly['Power (kW)'], width, label='Shifted Profile', color='red', alpha=0.7)
        ax2.axvspan(min(peak_hours)-0.5, max(peak_hours)+0.5, color='yellow', alpha=0.2, label='Peak Hours')
        ax2.set_title('Summer Load Profiles')
        ax2.set_xlabel('Hour of Day')
        ax2.set_ylabel('Power (kW)')
        ax2.set_xticks(x)
        ax2.set_xticklabels([str(i) for i in range(24)])
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        # Create subplots for irradiation profiles
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        x = np.arange(24)
        
        # Winter irradiation plot
        ax1.bar(x, winter_meteorological_df['Irradiation (kW/m^2)'], width, label='Solar Irradiation', color='orange', alpha=0.7)
        ax1.axvspan(min(peak_hours)-0.5, max(peak_hours)+0.5, color='yellow', alpha=0.2, label='Peak Hours')
        ax1.set_title('Winter Solar Irradiation Profile')
        ax1.set_xlabel('Hour of Day')
        ax1.set_ylabel('Irradiation (kW/m²)')
        ax1.set_xticks(x)
        ax1.set_xticklabels([str(i) for i in range(24)])
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Summer irradiation plot
        ax2.bar(x, summer_meteorological_df['Irradiation (kW/m^2)'], width, label='Solar Irradiation', color='orange', alpha=0.7)
        ax2.axvspan(min(peak_hours)-0.5, max(peak_hours)+0.5, color='yellow', alpha=0.2, label='Peak Hours')
        ax2.set_title('Summer Solar Irradiation Profile')
        ax2.set_xlabel('Hour of Day')
        ax2.set_ylabel('Irradiation (kW/m²)')
        ax2.set_xticks(x)
        ax2.set_xticklabels([str(i) for i in range(24)])
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()