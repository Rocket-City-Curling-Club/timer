![rccc_logo](./assets/rccc_logo.png)

# Rocket City Curling Club Draw Timer

## Running the timer

After installing dependencies from `requirements.txt` (Python 3.10+ recommended), the timer can be started by running
the following command:

`panel serve panel.py --args config.yaml`

where `config.yaml` is the path to a configuration file. See below for information on configuration options.

After running the command, navigate to `localhost:5006/panel` in the browser of your choice. To restart the
countdown, simply refresh the page.

For ease of use, it is recommended to create a bash script. A sample is provided below:

```bash
#!/bin/bash

cd timer

source venv/bin/activate

panel serve panel.py --args ./configs/bonspiel_config.yaml
```

Then, you can turn the bash script into an app launcher for easy start up.

### Hardware

At least 4 GB of RAM is recommended.

## Configuration options

The following configuration options are provided:

- `min_per_end`: Minutes per end for pacing, default 15.
- `countdown_min`: Starting value of countdown timer in minutes, default 105.
- `elapsed_min`: If timer is accidentally started late, adjust this value for minutes elapsed since the draw started. This allows the countdown to start later without affecting progress, default 0. This value needs to be reset back to 0 prior to beginning the next draw, so that it gets the full time!
- `zero_message`: Message to be displayed when the timer hits zero, default "FINISH THIS END".
- `max_min`: After hitting zero, the timer begins to count up. If this value is set, once `max_min` have elapsed (including countdown time), the timer stops counting completely and displays `max_message`. Default is `None`, timer will count up until stopped.
- `max_message`: Message to be displayed after `max_min` have elapsed. Default "TIME'S UP"
- `num_stones`: Total number of stones per end, default 16. Primarily modified for doubles.
- `total_ends`: Number of ends to include in progress bar, default 8.
- `progress_update_percentage`: Percentage difference between progress bar re-renders, default 5.

If a configuration option is not present in the configuration file, the default value will be used. Sample configs are provided in `./configs/`


