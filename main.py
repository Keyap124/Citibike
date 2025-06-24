import pandas as pd
from datetime import datetime

def analyze_station_reliability(file_path, station):
    # get data and extract hours
    df = pd.read_csv(file_path)
    df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
    df = df[df['station_name'] == station]

    if len(df) == 0:
        return f"No data for {station}"

    # calculate hourly stats
    hourly_stats = {}
    for hour, hour_data in df.groupby('hour'):
        hourly_stats[hour] = {
            'empty_bike_rate': (hour_data['available_bikes'] == 0).mean() * 100,
            'full_dock_rate': (hour_data['available_docks'] == 0).mean() * 100
        }

    # issue: >20% failure rate
    docking_issues = [
        f"{hour:02d}:00" 
        for hour, stats in hourly_stats.items() 
        if stats['full_dock_rate'] > 20
    ]
    renting_issues = [
        f"{hour:02d}:00" 
        for hour, stats in hourly_stats.items() 
        if stats['empty_bike_rate'] > 20
    ]

    # calculate availability score
    bike_avail_percent = round(100 * (1 - (df['available_bikes'] == 0).mean()), 1)
    dock_avail_percent = round(100 * (1 - (df['available_docks'] == 0).mean()), 1)

    return {
        "station": station,
        "bike_availability": bike_avail_percent,
        "dock_availability": dock_avail_percent,
        "is_reliable": bike_avail_percent > 80 and dock_avail_percent > 80,
        "docking_issues": docking_issues,
        "renting_issues": renting_issues,
        "hourly_stats": hourly_stats
    }

def format_station_analysis(result):
    # collect issue messages
    messages = []
    if result['renting_issues']:
        messages.append(f"Difficult to rent bikes at: {', '.join(result['renting_issues'])}")
    if result['docking_issues']:
        messages.append(f"Difficult to find empty docks at: {', '.join(result['docking_issues'])}")
    
    return (
        f"Station: {result['station']}\n"
        f"Average Hourly Bike Availability: {result['bike_availability']}%\n"
        f"Average Hourly Dock Availability: {result['dock_availability']}%\n"
        f"Status: {' AND '.join(messages) if messages else 'Reliable station at all hours'}"
    )

if __name__ == "__main__":
    # analyze each station
    for station in ["Downtown Hub", "Residential Park", "University Station", "Shopping Center"]:
        print(f"\n-- Analyzing {station} --")
        result = analyze_station_reliability("station_availability.csv", station)
        print(format_station_analysis(result))

        
