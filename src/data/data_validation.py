import os
import sys
import argparse
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] - %(message)s")

class DataValidator:
    def __init__(self, data_folder, output_folder):
        self.data_folder = data_folder
        self.output_folder = output_folder
        self.files_to_validate = {
            "agent_roster.csv": {
                "required_columns": ["agent_id", "users_first_name", "users_last_name", "users_office_location", "org_id"],
                "datetime_columns": []
            },
            "call_logs.csv": {
                "required_columns": ["call_id", "agent_id", "org_id", "installment_id", "status", "duration", "created_ts", "call_date"],
                "datetime_columns": ["call_date"]
            },
            "disposition_summary.csv": {
                "required_columns": ["call_date", "agent_id", "org_id", "login_time"],
                "datetime_columns": ["call_date"]
            }
        }
        os.makedirs(self.output_folder, exist_ok=True)

    def validate_and_save_all(self):
        validation_results = {}
        for file_name, rules in self.files_to_validate.items():
            file_path = os.path.join(self.data_folder, file_name)
            if not os.path.exists(file_path):
                msg = f"{file_name} does not exist in folder {self.data_folder}."
                logging.error(msg)
                validation_results[file_name] = [msg]
                continue
            try:
                df = pd.read_csv(file_path)
                self._validate_dataframe(df, file_name, rules["required_columns"], rules["datetime_columns"])
                df = self._add_missing_flag(df, rules["required_columns"], file_name)
                self._save_validated(df, file_name)
                validation_results[file_name] = []
            except Exception as e:
                msg = f"Failed to process {file_name}: {e}"
                logging.error(msg)
                validation_results[file_name] = [msg]
        self._log_summary(validation_results)

    def _validate_dataframe(self, df, file_name, required_columns, datetime_columns=None):
        # Check for presence of required columns; raise error if a critical column is missing.
        for col in required_columns:
            if col not in df.columns:
                msg = f"Critical column '{col}' is missing in {file_name}."
                logging.error(msg)
                raise ValueError(msg)
        # Flag missing entries in required columns
        for col in required_columns:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                msg = f"{missing_count} missing entries found in column '{col}' of {file_name}."
                logging.warning(msg)
        # Check for duplicate entries based on required columns
        duplicate_count = df.duplicated(subset=required_columns).sum()
        if duplicate_count > 0:
            msg = f"{duplicate_count} duplicates found based on columns {required_columns} in {file_name}."
            logging.warning(msg)
        # Validate datetime formatting for specified datetime columns
        if datetime_columns:
            for col in datetime_columns:
                try:
                    df[col] = pd.to_datetime(df[col], errors='raise')
                except Exception as e:
                    msg = f"Column '{col}' in {file_name} contains invalid date format: {e}"
                    logging.error(msg)

    def _add_missing_flag(self, df, required_columns, file_name):
        df["missing_flag"] = df[required_columns].isnull().any(axis=1)
        if df["missing_flag"].any():
            missing_rows = df["missing_flag"].sum()
            logging.warning(f"{missing_rows} rows in {file_name} have missing key values.")
        return df

    def _save_validated(self, df, file_name):
        output_file_path = os.path.join(self.output_folder, file_name)
        df.to_csv(output_file_path, index=False)
        logging.info(f"Validated data saved to: {output_file_path}")

    def _log_summary(self, validation_results):
        for file_name, messages in validation_results.items():
            if messages:
                logging.info(f"Validation issues for {file_name}:")
                for msg in messages:
                    logging.info(f"  - {msg}")
            else:
                logging.info(f"{file_name} passed all validations without issues.")

def main():
    parser = argparse.ArgumentParser(
        description="Data Validation Script: Validates agent_roster, call_logs, and disposition_summary files, adds a missing_flag column, and saves validated data."
    )
    parser.add_argument("--data_folder", type=str, default="data/loaded",
                        help="Path of the folder containing loaded CSV files.")
    parser.add_argument("--output_folder", type=str, default="data/validated",
                        help="Folder where the validated CSV files will be saved.")
    args = parser.parse_args()

    validator = DataValidator(args.data_folder, args.output_folder)
    validator.validate_and_save_all()

if __name__ == "__main__":
    main()