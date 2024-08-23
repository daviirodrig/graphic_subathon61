from generate_graph import generate_all_images, generate_video, interpolate_timer
from models import Result
from parse_logs import main as parse_logs

start_time, end_time = "2024-06-21T00:00:00.000Z", "2024-06-22T00:00:00.000Z"
logs = parse_logs("logs-05-01--02.log")
if logs is None:
    print("No logs found")
    exit(1)
print(f"Loaded {len(logs)} data points from logs")

results: list[Result] = []
for result in logs:
    if result.timestamp >= start_time and result.timestamp <= end_time:
        results.append(result)

print(f"Filtered {len(results)} data points within the specified time range")

interpolated_results = interpolate_timer(results)

generate_all_images(interpolated_results)

generate_video("images", "output_video.mp4")
