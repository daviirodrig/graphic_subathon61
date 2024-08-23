from datetime import datetime, timedelta
import os
import re
from typing import List, Union
from zoneinfo import ZoneInfo
from models import TimeEvent, UpdateTimerEvent, Result

full_json: List[Union[TimeEvent, UpdateTimerEvent]] = []


def parse_updates_log(lines: str) -> List[UpdateTimerEvent] | None:
    pattern = re.compile(
        r"(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z)\s+(?P<action>Adicionando para o timer:|Removendo do timer:|Timer atualizado:)\s+(?P<value>[0-9]*[.]?[0-9]*)",
        re.MULTILINE,
    )
    match = pattern.finditer(lines)
    full_result: List[UpdateTimerEvent] = []
    if not match:
        return None

    for match in match:
        match_dict = match.groupdict()
        if match_dict["action"] == "Adicionando para o timer:":
            action = "add"
            dick = UpdateTimerEvent(
                timestamp=match_dict["timestamp"],
                action=action,
                value=float(match_dict["value"]),
            )
        elif match_dict["action"] == "Removendo do timer:":
            action = "remove"
            dick = UpdateTimerEvent(
                timestamp=match_dict["timestamp"],
                action=action,
                value=float(match_dict["value"]),
            )
        elif match_dict["action"] == "Timer atualizado:":
            action = "update"
            now_ms = int(datetime.now().timestamp() * 1000)
            value = int(match_dict["value"]) - now_ms
            dick = UpdateTimerEvent(
                timestamp=match_dict["timestamp"],
                action=action,
                value=value,
            )
        else:
            raise ValueError("Invalid action")

        full_result.append(dick)

    return full_result


def main(filename: str):
    if not os.path.exists(filename):
        print(f"{filename} not found")
        return
    with open(filename, "r") as f:
        lines = f.read()
    updates = parse_updates_log(lines)
    if updates is None:
        print("No updates found in file")
        return None
    # Sync start point: April 30, 2024, 18:50 Sao Paulo time

    sync_time = datetime(
        2024, 4, 30, 18, 50, tzinfo=ZoneInfo("America/Sao_Paulo")
    ).astimezone(ZoneInfo("UTC"))
    sync_value = timedelta(hours=146, minutes=7, seconds=35)
    # 2024-07-12T16:10:06.160281444Z
    sync_time2 = datetime.fromisoformat("2024-07-12T16:09:06.160281444Z")
    sync_value2 = timedelta(hours=169, minutes=15, seconds=23)
    sync_time3 = datetime(
        2024, 7, 12, 3, 20, tzinfo=ZoneInfo("America/Sao_Paulo")
    ).astimezone(ZoneInfo("UTC"))
    sync_value3 = timedelta(hours=176, minutes=1, seconds=57)

    # Add the sync time as a update
    updates.append(
        UpdateTimerEvent(
            timestamp=sync_time.isoformat(),
            action="update",
            value=sync_value.total_seconds() * 1000,
        )
    )
    updates.append(
        UpdateTimerEvent(
            timestamp=sync_time2.isoformat(),
            action="update",
            value=sync_value2.total_seconds() * 1000,
        )
    )
    updates.append(
        UpdateTimerEvent(
            timestamp=sync_time3.isoformat(),
            action="update",
            value=sync_value3.total_seconds() * 1000,
        )
    )
    results: List[Result] = []
    current_timer = 0
    sorted_updates = sorted(updates, key=lambda x: x.timestamp)
    last_event = sorted_updates[0]
    with open('parse_logs.log', 'w') as log_file:
        log_file.write(f"Initial state: current_timer={current_timer}, last_event={last_event}\n")
        for update in sorted_updates:
            # Calculate time passed since last event
            upd_ms = datetime.fromisoformat(update.timestamp)
            last_ms = datetime.fromisoformat(last_event.timestamp)
            time_passed = upd_ms - last_ms
            # Calculate time passed in milliseconds
            time_passed_ms = int(time_passed.total_seconds() * 1000)
            current_timer -= time_passed_ms
            last_event = update

            log_file.write(f"Processing update: {update}\n")
            log_file.write(f"Time passed: {time_passed_ms}ms\n")
            log_file.write(f"Current timer before action: {current_timer}\n")

            if update.action == "add":
                current_timer += update.value
                log_file.write(f"Adding {update.value}ms to timer\n")
            elif update.action == "remove":
                current_timer -= update.value
                log_file.write(f"Removing {update.value}ms from timer\n")
            elif update.action == "update":
                current_timer = update.value
                log_file.write(f"Updating timer to {update.value}ms\n")
            else:
                raise ValueError("Invalid action")

            log_file.write(f"Current timer after action: {current_timer}\n")

            results.append(
                Result(
                    timestamp=update.timestamp,
                    action=update.action,
                    timer=current_timer,
                    value=update.value,
                )
            )
            log_file.write(f"Appended result: {results[-1]}\n")
            log_file.write("---\n")
    # with open("output.json", "w") as f:
    #     dicts = [asdict(x) for x in results]
    #     f.write(json.dumps(dicts, indent=2, ensure_ascii=False))
    return results
