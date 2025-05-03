import os
import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] - %(message)s")

class FeatureEngineer:
    def __init__(self, input_path, output_folder):
        self.input_path = input_path
        self.output_folder = output_folder
        # Save as agent_performance_summary.csv as requested
        self.output_path = os.path.join(output_folder, "agent_performance_summary.csv")
        os.makedirs(output_folder, exist_ok=True)
        self.df = None
        self.features = None

    def load_data(self):
        self.df = pd.read_csv(self.input_path)
        if "call_date" in self.df.columns:
            self.df["call_date"] = pd.to_datetime(self.df["call_date"], errors="coerce")
        else:
            logging.error("'call_date' column missing in merged data.")
            raise ValueError("'call_date' column missing in merged data.")
        # Ensure all required columns exist
        for col in ["installment_id", "status", "duration", "login_time"]:
            if col not in self.df.columns:
                self.df[col] = np.nan

    def compute_total_calls(self):
        return self.df.groupby(["agent_id", "call_date"]).size().rename("total_calls")

    def compute_completed_calls(self):
        # Count calls with status == 'Completed'
        return (
            self.df[self.df["status"].astype(str).str.lower() == "completed"]
            .groupby(["agent_id", "call_date"])
            .size()
            .rename("completed_calls")
        )

    def compute_unique_loans(self):
        return (
            self.df.groupby(["agent_id", "call_date"])["installment_id"]
            .nunique()
            .rename("unique_loans_contacted")
        )

    def compute_avg_call_duration(self, total_calls):
        # Convert duration to minutes if needed
        if self.df["duration"].dropna().max() > 1000:
            self.df["duration_min"] = self.df["duration"] / 60
        else:
            self.df["duration_min"] = self.df["duration"]
        avg_call_duration = (
            self.df.groupby(["agent_id", "call_date"])["duration_min"]
            .sum() / total_calls
        ).rename("avg_call_duration_min")
        return round(avg_call_duration, 2)

    def compute_presence(self):
        return (
            self.df.groupby(["agent_id", "call_date"])["login_time"]
            .apply(lambda x: int(x.notnull().any()))
            .rename("presence")
        )

    def engineer_features(self):
        total_calls = self.compute_total_calls()
        completed_calls = self.compute_completed_calls()
        unique_loans = self.compute_unique_loans()
        avg_call_duration = self.compute_avg_call_duration(total_calls)
        presence = self.compute_presence()

        features = pd.concat([total_calls, unique_loans, completed_calls, avg_call_duration], axis=1).fillna(0)
        features["connect_rate"] = round(features["completed_calls"] / features["total_calls"], 2)
        features["connect_rate"] = features["connect_rate"].fillna(0)
        features = features.reset_index()
        features["presence"] = presence.reset_index(drop=True)
        # Ensure presence is last column
        cols = [col for col in features.columns if col != "presence"] + ["presence"]
        self.features = features[cols]

    def save_features(self):
        self.features.to_csv(self.output_path, index=False)
        logging.info(f"Feature engineered data saved to {self.output_path}")

def main():
    input_path = "data/merged/merged_data.csv"
    output_folder = "data/featured"
    fe = FeatureEngineer(input_path, output_folder)
    fe.load_data()
    fe.engineer_features()
    fe.save_features()

if __name__ == "__main__":
    main()