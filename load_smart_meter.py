import pandas as pd
import os

def main():
    # Define the path to the specific CSV file
    file_path = os.path.join("data", "smart_meter_data.csv")
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    try:
        # Load the CSV file into a DataFrame
        df = pd.read_csv(file_path)
        
        # Print the column names
        print("--- Column Names ---")
        for col in df.columns:
            print(f" - {col}")
            
        # Print the total number of rows
        print(f"\nTotal Rows: {len(df)}")
        
        # Display the first 5 rows
        print("\n--- First 5 Rows ---")
        print(df.head())
        
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")

if __name__ == "__main__":
    main()
