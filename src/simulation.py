import numpy as np

def interpolate_telemetry(telemetry, steps=500):
    telemetry = telemetry.copy()

    # converter tempo para segundos
    telemetry['TimeSeconds'] = telemetry['Time'].dt.total_seconds()

    time = telemetry['TimeSeconds'].values
    x = telemetry['X'].values
    y = telemetry['Y'].values

    # nova base de interpolação -> tempo
    time_new = np.linspace(time.min(), time.max(), steps)

    x_interp = np.interp(time_new, time, x)
    y_interp = np.interp(time_new, time, y)

    # manter divisão em 3 setores (aproximação visual)
    sector_points = steps // 3


    sectors = np.array(
        [1] * sector_points +
        [2] * sector_points +
        [3] * (steps - 2 * sector_points)
    )

    return x_interp, y_interp, time_new, sectors