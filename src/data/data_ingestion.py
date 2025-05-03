import os
import sys
import argparse
import pandas as pd
import numpy as np
from src.logger import logging

pd.set_option('future.no_silent_downcasting', True)

class DataIngestion:
    def __init__(self, input_folder="input_data", output_folder="data"):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.files = ["agent_roster.csv", "call_logs.csv", "disposition_summary.csv"]
        os.makedirs(self.output_folder, exist_ok=True)

    def load_data(self, file_path):
        try:
            df = pd.read_csv(file_path)
            logging.info(f"Data loaded successfully from {file_path}")
            return df
        except Exception as e:
            logging.error(f"Failed to load data from {file_path}: {e}")
            raise

    def save_data(self, df, file_path):
        try:
            df.to_csv(file_path, index=False)
            logging.info(f"Data saved successfully to {file_path}")
        except Exception as e:
            logging.error(f"Failed to save data to {file_path}: {e}")
            raise

    def process_files(self):
        for file in self.files:
            input_file_path = os.path.join(self.input_folder, file)
            output_file_path = os.path.join(self.output_folder, file)
            logging.info(f"Processing file: {file}")
            df = self.load_data(input_file_path)
            # Additional processing can be added here if needed
            self.save_data(df, output_file_path)

def main():
    parser = argparse.ArgumentParser(
        description="Data ingestion script that loads CSV files from an input folder and saves them into an output folder."
    )
    parser.add_argument(
        "--input_folder", type=str, default="input_data",
        help="Folder path containing the raw CSV files."
    )
    parser.add_argument(
        "--output_folder", type=str, default="data",
        help="Folder path where the processed CSV files will be saved."
    )
    args = parser.parse_args()

    ingestion = DataIngestion(args.input_folder, args.output_folder)
    ingestion.process_files()

if __name__ == "__main__":
    main()
