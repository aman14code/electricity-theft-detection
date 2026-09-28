import pandas as pd
import glob
import os

def main():
    # Define the path to the data directory
    data_dir = "data"
    
    # Use glob to find all CSV files in the data directory
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in the '{data_dir}' directory.")
        return

    print(f"Found {len(csv_files)} CSV files. Combining...")

    # Read each CSV file into a DataFrame and append to a list
    dfs = []
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            dfs.append(df)
        except Exception as e:
            print(f"Error reading {file}: {e}")

    if not dfs:
        print("No valid data could be read from the CSV files.")
        return

    # Combine all DataFrames into a single DataFrame
    combined_df = pd.concat(dfs, ignore_index=True)

    # Print the total row count and column names
    print("\n--- Summary ---")
    print(f"Total Rows: {len(combined_df)}")
    print(f"Total Columns: {len(combined_df.columns)}")
    print("\nColumn Names:")
    for col in combined_df.columns:
        print(f" - {col}")

if __name__ == "__main__":
    main()
