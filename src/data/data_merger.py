import os
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] - %(message)s")

class DataMerger:
    def __init__(self, data_folder="data/loaded", output_folder="data/merged"):
        self.data_folder = data_folder
        self.output_folder = output_folder
        os.makedirs(self.output_folder, exist_ok=True)

    def load_data(self):
        self.agent_roster = pd.read_csv(os.path.join(self.data_folder, "agent_roster.csv"))
        self.call_logs = pd.read_csv(os.path.join(self.data_folder, "call_logs.csv"))
        self.disposition_summary = pd.read_csv(os.path.join(self.data_folder, "disposition_summary.csv"))

    def preprocess_dates(self):
        for df, name in [(self.call_logs, "call_logs"), (self.disposition_summary, "disposition_summary")]:
            if "call_date" in df.columns:
                df["call_date"] = pd.to_datetime(df["call_date"], errors="coerce")
            else:
                logging.warning(f"'call_date' not found in {name}")

    def merge_data(self):
        # Merge call_logs and disposition_summary on agent_id, org_id, call_date (outer join)
        merged_calls = pd.merge(
            self.call_logs, self.disposition_summary,
            on=["agent_id", "org_id", "call_date"],
            how="outer",
            suffixes=('_call', '_disp')
        )
        # Merge with agent_roster on agent_id and org_id (outer join)
        merged_all = pd.merge(
            merged_calls, self.agent_roster,
            on=["agent_id", "org_id"],
            how="outer"
        )
        return merged_all

    def log_mismatches(self, merged_df):
        missing_rows = merged_df[merged_df.isnull().any(axis=1)]
        if not missing_rows.empty:
            logging.warning(f"{len(missing_rows)} rows have missing values after merging. These indicate mismatches between datasets.")

    def save_merged(self, merged_df):
        output_path = os.path.join(self.output_folder, "merged_data.csv")
        merged_df.to_csv(output_path, index=False)
        logging.info(f"Merged data saved to {output_path}")

    def explain_join_logic(self):
        print(
            "Join Logic: Outer joins are used to ensure no data loss. "
            "Any row present in any dataset will appear in the merged result. "
            "Rows with missing values after the merge indicate mismatches (i.e., records present in one file but not in others)."
        )

    def run(self):
        self.load_data()
        self.preprocess_dates()
        merged_df = self.merge_data()
        self.log_mismatches(merged_df)
        self.save_merged(merged_df)
        self.explain_join_logic()

def main():
    merger = DataMerger()
    merger.run()

if __name__ == "__main__":
    main()