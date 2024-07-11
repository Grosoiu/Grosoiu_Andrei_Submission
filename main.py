import os
import sys
import pandas as pd
import random
import numpy as np
from datetime import datetime

timestamp = datetime.now()

def read_csv_files(num_files):
    """
    Reads one or two files for each stock exchange (provided by cli argument) and returns 30 datapoints
    starting from a random timestamp. Creates a dictonary that has the stock exchange name as key and the value
    is a list of dataframes.

    Parameters:
        num_files (int): Number of files to read (1 or 2).

    Returns:
        dict: A dictionary with the directory names as keys and a list of dataframes with 30 datapoints each as values.
    """
    assert num_files in [1, 2], "Number of files must be either 1 or 2."
    
    input_dir = 'inputs'
    result = {}

    for exchange in os.listdir(input_dir):
        exchange_dir = os.path.join(input_dir, exchange)
        if not os.path.isdir(exchange_dir):
            print(f"LOG LEVEL : WARNING, there are additional files outside of stock exchange directories, timestamp: {timestamp}.")
            continue

        csv_files = [f for f in os.listdir(exchange_dir) if f.endswith('.csv')]
        if not csv_files:
            print(f"No CSV files found in {exchange_dir}.")
            print(f"LOG LEVEL: WARNING, there are no csv files in the stock exchange directory, timestamp: {timestamp}.")
            continue

        selected_files = csv_files[:num_files] # Select the first 1-2 csv files from the directory
        exchange_dataframes_list = []

        for file in selected_files:
            file_path = os.path.join(exchange_dir, file)
            try:
                df = pd.read_csv(file_path, header=None, names=["ID","Timestamp","Price"])
                if df.empty:
                    print(f"LOG LEVEL: CRITICAL, there is an empty CSV file in the inputs directory, timestamp: {timestamp}.")
                    raise ValueError("CSV file is empty")      
                if len(df) < 30:
                    print(f"LOG LEVEL: CRITICAL, one of the CSV files has less than 30 data points, timestamp: {timestamp}.")
                    raise ValueError("Number of data points is not enough for processing")
                start = random.randint(0, len(df) - 30)
                sampled_data = df.iloc[start:start + 30]
                exchange_dataframes_list.append(sampled_data)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                return None
        if exchange_dataframes_list:
            result[exchange] = exchange_dataframes_list          
    return result

def parse_exchanges(processed_data):
    """
    Processes the sampled data to identify outliers and creates CSV files with outlier information.

    Parameters:
        data (dict): A dictionary with directory names as keys and lists of dataframes with 30 datapoints each as values.
    """
    output_dir = 'output'
    # os.makedirs(output_dir, exist_ok=True)
    for exchange, data_frame_list in processed_data.items():
        outlier_list = []
        for item in data_frame_list:
            try:
                tag = item['ID'].unique()[0]
                mean = item["Price"].mean()
                std = item["Price"].std()
                threshold = 2 * std
                item["Mean"] = mean
                item["Deviation"] = item["Price"] - mean
                item["% Deviation"] = (item["Deviation"] / mean) * 100
                outliers = item[np.abs(item["Deviation"]) > threshold]
                outlier_list.append(outliers)
                if not outliers.empty:
                    output_file = os.path.join(output_dir, f"{exchange}_{tag}_outliers.csv")
                    outliers.to_csv(output_file, index=False)
                    print(f"LOG LEVEL: INFO, outliers saved to {output_file}, timestamp: {timestamp}.")
                else:
                    print(f"No outliers found when processing {tag}")
                    
            except Exception as e:
                print(f"Error: {e}")
                return None
    

if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        print("Usage: python main.py <num_files>")
        sys.exit(1)

    num_files = int(sys.argv[1])
    data = read_csv_files(num_files)
    parse_exchanges(data)
