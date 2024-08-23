import re
from models import Result
from datetime import datetime, timedelta

from zoneinfo import ZoneInfo
import matplotlib.pyplot as plt
import numpy as np

import os
import shutil
import sys
import matplotx
from moviepy.editor import ImageSequenceClip


def interpolate_timer(results: list[Result]) -> list[Result]:
    """
    Interpolate timer values between existing results.

    This function takes a list of Result objects and interpolates additional
    Result objects between each pair of consecutive results. The interpolation
    is done for every 60 seconds between two consecutive timestamps.

    Args:
        results (list[Result]): A list of Result objects to interpolate.

    Returns:
        list[Result]: A new list of Result objects including the original and
        interpolated results.

    Side effects:
        - Prints progress messages to the console.
    """
    print("Starting interpolation...")
    interpolated_results = []
    for i in range(len(results)):
        interpolated_results.append(results[i])
        if i < len(results) - 1:
            current_time = datetime.fromisoformat(results[i].timestamp)
            next_time = datetime.fromisoformat(results[i + 1].timestamp)
            time_diff = (next_time - current_time).total_seconds()
            timer_diff = results[i + 1].timer - results[i].timer

            # Add interpolated points every 60 seconds
            for j in range(1, int(time_diff / 60)):
                interpolated_time = current_time + timedelta(seconds=j * 60)
                interpolated_timer = results[i].timer + (
                    timer_diff * (j * 60 / time_diff)
                )
                interpolated_results.append(
                    Result(
                        timestamp=interpolated_time.isoformat(),
                        action="update",
                        value=0,
                        timer=interpolated_timer,
                    )
                )
    print(f"Interpolation complete. Total points: {len(interpolated_results)}")
    # with open("interpolated.json", "w") as f:
    #     dicts = [asdict(x) for x in interpolated_results]
    #     f.write(json.dumps(dicts, indent=2, ensure_ascii=False))
    return interpolated_results


def generate_graph_png(
    folder: str,
    timer: float,
    current_time: str,
    full_length: int,
    timeList: list = [],
) -> list:
    x = len(timeList)
    timer_h = int(timer / 3600000)
    timer_m = int((timer - timer_h * 3600000) / 60000)
    timer_s = int((timer - timer_h * 3600000 - timer_m * 60000) / 1000)
    current_time = (
        datetime.fromisoformat(current_time)
        .astimezone(ZoneInfo("America/Sao_Paulo"))
        .strftime("%d/%m %H:%M:%S")
    )
    timer_str = f"{timer_h:03}:{timer_m:02}:{timer_s:02}"
    filename = f"{folder}/graph_{x}.png"

    print(f"{timer_str} -> {filename} {x}/{full_length}")

    timeList.insert(x, timer_h)
    ypoints = np.array(timeList)
    with plt.style.context(matplotx.styles.duftify(matplotx.styles.github["dark"])):
        plt.plot(ypoints)
        plt.text(
            x=0.25,
            y=1.05,
            s=f"{current_time}",
            transform=plt.gca().transAxes,
            fontsize=14,
            verticalalignment="top",
            horizontalalignment="center",
            color="white",
        )
        plt.text(
            0.75,
            1.05,
            f"{timer_str}",
            transform=plt.gca().transAxes,
            fontsize=14,
            verticalalignment="top",
            horizontalalignment="center",
            color="white",
        )

        plt.savefig(filename)
        plt.clf()
    return timeList


def generate_all_images(interpolated_results: list[Result]) -> None:
    folder = "images"

    if os.path.exists(folder):
        choice_delete = input(
            "do you want to delete the folder and continue? (yes or no): "
        )
        if choice_delete == "yes":
            print("ok! deleting the folder...")
            shutil.rmtree(folder, ignore_errors=False)
            os.makedirs(folder)
            print("program starting!")
        if choice_delete == "no":
            print("ok! stopping now.")
            sys.exit()
    else:
        os.makedirs(folder)

    timeList: list = []
    for i in interpolated_results:
        timeList = generate_graph_png(
            folder,
            i.timer,
            i.timestamp,
            len(interpolated_results),
            timeList,
        )


def generate_video(images_folder: str, video_name: str):
    def extract_number(filename):
        match = re.search(r"\d+", filename)
        return int(match.group()) if match else -1

    images = sorted(
        [f"{images_folder}/{img}" for img in os.listdir(images_folder)],
        key=lambda x: extract_number(os.path.join(images_folder, x)),
    )

    clip = ImageSequenceClip(images, fps=30)
    clip.write_videofile(video_name, codec="libx264")
