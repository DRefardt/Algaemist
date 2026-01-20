import pandas as pd
import plotly.express as px
import os


# Define Y-axis ranges for each variable
y_axis_ranges = {
    "temp": (0, 45),
    "pH": (2, 12),
    "light_prim": (0, 850),
    "light_sec": (0, 850),
    "air": (0, 1000),
    "co2": (0, 200),
    "turb_pump": (0, 100)
}

# Define units for each variable
y_axis_units = {
    "temp": "°C",
    "pH": "",
    "light_prim": "",
    "light_sec": "",
    "air": "ml/min",
    "co2": "ml/min",
    "turb_pump": "%"
}

def main():
    # Ask user for CSV path
    csv_path = input("Enter path to CSV file: ").strip()
    if not os.path.exists(csv_path):
        print("File not found.")
        return

    # Load CSV
    df = pd.read_csv(csv_path)

    # Ask user which columns to plot
    print("\nAvailable columns:", list(df.columns))
    x_col = input("Select X column: ").strip()
    y_col = input("Select Y column: ").strip()

    if x_col not in df.columns or y_col not in df.columns:
        print("Invalid column selection.")
        return

    # Optional: ask for hover column
    hover_col = input("Optional hover column (press Enter to skip): ").strip()
    if hover_col not in df.columns:
        hover_col = None

    # Create Y-axis label including units if available
    y_label = y_col
    if y_col in y_axis_units and y_axis_units[y_col]:
        y_label += f" [{y_axis_units[y_col]}]"
    
    # Create scatter/point plot
    fig = px.scatter(df, x=x_col, y=y_col, hover_data=[hover_col] if hover_col else None,
                     title=f"{y_col} vs {x_col}", labels={y_col: y_label})
    
    # Apply Y-axis range if available
    if y_col in y_axis_ranges:
        fig.update_yaxes(range=y_axis_ranges[y_col])
        
    # Show plot in browser
    fig.show()

if __name__ == "__main__":
    main()