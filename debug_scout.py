
import data_fetcher
scout = data_fetcher.get_today_scout()
print("Scout for today:")
print(scout)
history = data_fetcher.get_history_games()
print(f"Total history entries: {len(history)}")
print("First 2 entries:")
print(history[:2])
