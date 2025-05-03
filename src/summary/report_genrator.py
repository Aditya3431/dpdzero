import os
import pandas as pd
from datetime import datetime

class SlackSummaryReport:
    def __init__(self, perf_path, agent_info_path, report_folder="report"):
        self.perf_path = perf_path
        self.agent_info_path = agent_info_path
        self.report_folder = report_folder
        os.makedirs(self.report_folder, exist_ok=True)
        self.df = None
        self.agent_info_df = None

    def load_data(self):
        self.df = pd.read_csv(self.perf_path)
        self.agent_info_df = pd.read_csv(self.agent_info_path)
        self.df["call_date"] = self.df["call_date"].astype(str)

    def get_top_performer(self, df_day):
        if df_day.empty:
            return None, None
        top_row = df_day.loc[df_day["connect_rate"].idxmax()]
        agent_id = top_row["agent_id"]
        connect_rate = round(top_row["connect_rate"] * 100)
        agent_row = self.agent_info_df[self.agent_info_df["agent_id"] == agent_id]
        if not agent_row.empty:
            agent_name = f"{agent_row.iloc[0]['users_first_name']} {agent_row.iloc[0]['users_last_name']}"
        else:
            agent_name = agent_id
        return agent_name, connect_rate

    def get_total_active_agents(self, df_day):
        return df_day[df_day["presence"] == 1]["agent_id"].nunique()

    def get_average_duration(self, df_day):
        return round(df_day["avg_call_duration_min"].mean(), 1)

    def generate_summary(self, report_date):
        df_day = self.df[self.df["call_date"] == report_date]
        if df_day.empty:
            return f"No data available for {report_date}."
        agent_name, connect_rate = self.get_top_performer(df_day)
        total_active_agents = self.get_total_active_agents(df_day)
        avg_duration = self.get_average_duration(df_day)
        msg = (
            f"Agent Summary for {report_date}\n"
            f"Top Performer: {agent_name} ({connect_rate}% connect rate)\n"
            f"Total Active Agents: {total_active_agents}\n"
            f"Average Duration: {avg_duration} min"
        )
        return msg

    def save_report(self, summary, report_date):
        report_path = os.path.join(self.report_folder, f"{report_date}.txt")
        with open(report_path, "w") as f:
            f.write(summary)
        print(f"Report saved to {report_path}")
        print(f"✅ Your Slack-style summary has been saved at: {os.path.abspath(report_path)}")

def main():
    perf_path = "data/featured/agent_performance_summary.csv"
    agent_info_path = "data/loaded/agent_roster.csv"
    report_folder = "report"

    # Prompt user for date input
    user_date = input("Enter the date for the report in YYYY-MM-DD format (e.g., 2025-04-28): ").strip()

    # Validate date format
    try:
        datetime.strptime(user_date, "%Y-%m-%d")
    except ValueError:
        print("❌ Invalid date format. Please use YYYY-MM-DD (e.g., 2025-04-28).")
        return

    report = SlackSummaryReport(perf_path, agent_info_path, report_folder)
    report.load_data()
    summary = report.generate_summary(user_date)
    report.save_report(summary, user_date)

if __name__ == "__main__":
    main()