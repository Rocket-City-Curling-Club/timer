import argparse
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import panel as pn
import yaml
from matplotlib.patches import Rectangle
from pathlib import Path

ASSETS_DIR = Path("./assets")
STONE_WIDTH = 150
PROGRESS_WIDTH = 175

matplotlib.use('agg')


class CountdownTimer:
    def __init__(self, config):
        self.num_stones = config.get("num_stones", 16)
        self.total_ends = config.get("total_ends", 8)
        self.s_per_end = int(config.get("min_per_end", 15) * 60)
        self.duration_s = int(config.get("countdown_min", 105) * 60)
        self.remaining_s = self.duration_s - int(config.get("elapsed_min", 0) * 60)
        self.elapsed_min = (self.duration_s - self.remaining_s) // 60
        self.zero_message = config.get("zero_message", "FINISH THIS END")
        self.elapsed_out_file = config.get("elapsed_min_out_file", None)
        max_min = config.get("max_min", None)
        if max_min is not None:
            self.max_s = int(max_min) * 60
        else:
            self.max_s = None
        self.max_message = config.get("max_message", "TIME'S UP")
        self.progress_update_percentage = config.get("progress_update_percentage", 5)
        self.s_per_stone = self.s_per_end / self.num_stones
        self.curr_stone_idx = 0

        self.countdown_text = pn.pane.HTML(
            self.timer_text(self.remaining_s),
            sizing_mode="stretch_width",
            margin=(-450, 0, -150, 0),
        )
        self.zero_message_html = pn.pane.HTML(
            f"<p style='text-align: center; color: white; font-size: 8vw'>" \
            f"{self.zero_message}</p>",
            margin=(-200, 0, -125, 0),
        )
        self.zero_message_html.visible = False
        self.max_message_html = pn.pane.HTML(
            f"<p style='text-align: center; color: white; font-size: 8vw'>" \
            f"{self.max_message}</p>",
            margin=(50, 0, -125, 0),
        )
        self.max_message_html.visible = False

        self.end_progress = [-self.progress_update_percentage] * self.total_ends
        self.end_progress_figs = [None] * self.total_ends
        self.progress = pn.Row(margin=0)

        self.rock_grid = pn.GridBox(
            *[pn.pane.PNG(ASSETS_DIR / "stone.png", width=STONE_WIDTH) for _ in range(self.num_stones)],
            ncols=int(self.num_stones / 2),
        )
        # Remap row-based indices to columns
        stones_per_team = int(self.num_stones / 2)
        def _iteration_order():
            for i in range(stones_per_team):
                yield i
                yield i + stones_per_team
        self.rock_idx_mapping = {idx: mapped_idx for idx, mapped_idx in enumerate(_iteration_order())}
        self.rock_pacing = pn.Row(
            pn.layout.HSpacer(),
            self.rock_grid,
            pn.layout.HSpacer(),
        )
        self.rccc_logo = pn.Row(
            pn.HSpacer(),
            pn.pane.PNG(ASSETS_DIR / "rccc_logo.png", width=STONE_WIDTH, margin=(-100, 50, 0, 0)),
        )

        self.content = pn.Column(
            pn.layout.VSpacer(),
            self.countdown_text,
            self.zero_message_html,
            self.max_message_html,
            self.progress,
            self.rock_pacing,
            self.rccc_logo,
            pn.layout.VSpacer(),
            styles={'background-color': 'green'},
        )

        self.remaining_s += 1
        self.update_countdown()
        self.update_rock_pacing(init=True)

    def update_progress_bar(self):
        """Progress bar fill"""
        segments = []

        elapsed_time_s = self.duration_s - self.remaining_s
        end = elapsed_time_s // self.s_per_end + 1
        section_width = 100 / self.total_ends

        for e in range(self.total_ends):
            # Calculate how much the current section should be filled
            fill_percentage = int(min(100, max(0, (elapsed_time_s - e * self.s_per_end) / self.s_per_end * 100)))
            if (
                fill_percentage >= (self.end_progress[e] + self.progress_update_percentage) or
                (fill_percentage == 100 and self.end_progress[e] != 100)
            ):
                self.end_progress[e] = fill_percentage
            else:
                continue

            # Calculate how much the current section should be filled
            fill_percentage = int(min(100, max(0, (elapsed_time_s - e * self.s_per_end) / self.s_per_end * 100)))
            if fill_percentage != self.end_progress[e]:
                self.end_progress[e] = fill_percentage

            text = f"{e+1}"

            # Create a figure and axis
            fig, ax = plt.subplots(figsize=(1, 1))

            # Create an image with two background colors to fill with background colors
            image = np.zeros((100, 100, 3))

            # Completed fill
            image[:, :fill_percentage] = [0.6, 0.6, 0.6]  # RGB for grey

            # Incomplete fill
            image[:, fill_percentage:] = [1, 1, 1]  # RGB for white

            ax.imshow(image)

            # Remove the white border by adjusting the layout
            plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

            # Add text centered on the image
            ax.text(0.5, 0.5, f'{text}', color='black', fontsize=50, ha='center', va='center', transform=ax.transAxes)

            ax.axis('off')

            # Add a black outline using a rectangle
            rect = Rectangle((0, 0), 1, 1, linewidth=4, edgecolor='black', facecolor='none', transform=ax.transAxes)
            ax.add_patch(rect)

            matplotlib_pane = pn.pane.Matplotlib(fig, margin=0, width=PROGRESS_WIDTH)
            self.end_progress_figs[e] = matplotlib_pane
            plt.close()

        self.progress.objects = [
            pn.layout.HSpacer(),
            *self.end_progress_figs,
            pn.layout.HSpacer(),
        ]

    def timer_text(self, t_s):
        """Timer display text"""
        secs = t_s

        # Start counting up after 0
        color = "black"
        prefix = ""
        message_html = ""
        font_size = 500
        if t_s <= 0:
            secs *= -1
            prefix = "+"
            color = "white"
            font_size = 400

        # Convert to hours:mins:seconds
        mins, secs = divmod(secs, 60)
        hours, mins = divmod(mins, 60)

        html = f"<h1 style='text-align: center; color: {color}; font-size: 23vw'>" \
            f"{prefix}{hours:01d}:{mins:02d}:{secs:02d}</h1>"

        return html

    def update_rock_pacing(self, init=False):
        """Determine which rocks should have been thrown at this point"""
        if self.curr_stone_idx == 0:
            self.rock_grid.objects = [
                pn.pane.PNG(ASSETS_DIR / "stone.png", width=STONE_WIDTH) for _ in range(self.num_stones)
            ]
        elif init:  # Refresh all images
            imgs = [
                pn.pane.PNG(ASSETS_DIR / "stone.png", width=STONE_WIDTH)
                for _ in range(self.num_stones)
            ]
            for i in range(self.curr_stone_idx):
                imgs[self.rock_idx_mapping[i]] = pn.pane.PNG(ASSETS_DIR / "thrown_stone.png", width=STONE_WIDTH)
            self.rock_grid.objects = imgs
        else:
            self.rock_grid[self.rock_idx_mapping[self.curr_stone_idx-1]] = pn.pane.PNG(
                ASSETS_DIR / "thrown_stone.png", width=STONE_WIDTH
            )


    def update_countdown(self):
        """Main update controller, runs every second"""
        self.remaining_s -= 1

        self.countdown_text.object = self.timer_text(self.remaining_s)
        if self.remaining_s <= 0:
            self.content.styles = {'background-color': '#FF0000'}  # Change background color to red
        elif self.remaining_s < 900:  # change to yellow with 15 mins (900s) left
            self.content.styles = {'background-color': '#FFFF00'}
        else:
            self.content.styles = {'background-color': "#99FF99"}

        # Compute which stone we should be on
        elapsed_time_s = self.duration_s - self.remaining_s
        previous_stone_idx = self.curr_stone_idx
        self.curr_stone_idx = int(elapsed_time_s // self.s_per_stone % self.num_stones)

        # Write out elapsed min if different and configured to do so
        elapsed_min = elapsed_time_s // 60
        if self.elapsed_out_file is not None and elapsed_min != self.elapsed_min:
            self.elapsed_min = elapsed_min
            with open(self.elapsed_out_file, "w") as f:
                f.write(f"{elapsed_min}")

        # Stone pacing
        if self.remaining_s <= 0:
            self.rock_grid.visible = False
        elif previous_stone_idx != self.curr_stone_idx:
            self.update_rock_pacing()

        # Progress bar
        if self.max_s is not None and elapsed_time_s >= self.max_s:
            self.countdown_text.visible = False
            self.zero_message_html.visible = False
            self.progress.visible = False
            self.max_message_html.visible = True
        elif self.remaining_s <= 0:
            self.progress.visible = False
            self.zero_message_html.visible = True
        else:
            self.update_progress_bar()

    def start(self):
        # Add a periodic callback to update the countdown every second
        self.periodic_callback = pn.state.add_periodic_callback(self.update_countdown, 1000)  # 1000 ms = 1 second


def main():
    parser = argparse.ArgumentParser(description ='Draw timer')
    parser.add_argument(
        "config_file",
        type=Path,
        help="Path to yaml config file"
    )
    args = parser.parse_args()

    with open(args.config_file, "r") as config_file:
        config = yaml.safe_load(config_file)

    # Create a countdown timer instance
    timer = CountdownTimer(config)

    # Start the countdown immediately
    timer.start()

    # Layout the Panel
    timer.content.servable(title="RCCC Draw Timer")


if __name__ == "__main__" or __name__.startswith("bokeh"):
    main()
