from typing import Generator
from zoneinfo import ZoneInfo
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

import os
import shutil
import sys
import json
import matplotx

timeList = []
x = 0

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


def getTime() -> Generator[tuple[float, str], None, None]:
    with open("interpolated.json") as f:
        data = json.load(f)
        for i in data:
            yield i["timer"], i["timestamp"]


times = getTime()
for i in times:
    timer, current_time = i
    timer_h = int(timer / 3600000)
    timer_m = int((timer - timer_h * 3600000) / 60000)
    timer_s = int((timer - timer_h * 3600000 - timer_m * 60000) / 1000)
    current_time = (
        datetime.fromisoformat(current_time)
        .astimezone(ZoneInfo("America/Sao_Paulo"))
        .strftime("%d/%m %H:%M:%S")
    )
    timer_str = f"{timer_h:03}:{timer_m:02}:{timer_s:02}"

    print(f"{timer_h}, {x}")

    timeList.insert(x, timer_h)
    ypoints = np.array(timeList)
    x = x + 1
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

        plt.savefig(f"{folder}/graph_{x}.png")
        plt.clf()
