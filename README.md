# PulseGen Client

This is a client for the
[Qynit.PulseGen.Server](https://github.com/kahojyun/Qynit.PulseGen)

## Installation

1. Clone this repository
```bash
git clone https://github.com/kahojyun/Qynit.PulseGen.git
```
2. Install
```bash
pip install .
```

## Usage

First, start the server following the instruction in
[Qynit.PulseGen.Server](https://github.com/kahojyun/Qynit.PulseGen)

```shell
dotnet run --urls http://localhost:5200 --project ./src/Qynit.PulseGen.Server -c Release
```

Then, run the following code in python

```python
import numpy as np
from matplotlib import pyplot as plt
from pulsegen_client import PulseGenClient, RequestBuilder

builder = RequestBuilder()

# channel_name, carrier_freq, sample_rate, delay, number_of_points, alignment_level
builder.add_channel("ch1", 130e6, 2e9, 0, 100000, -4)
builder.add_channel("ch2", 0, 1e9, 100e-9, 50000, -4)
x = np.linspace(0, np.pi, 11)
y = np.sin(x)
xx = np.linspace(-0.5, 0.5, 11)
# x values should be in the range of [-0.5, 0.5]
builder.add_interpolated_shape("halfcos", xx, y)

for i in range(900):
    # start_time, channel_name, amplitude, shape_name, width, [plateau, drag_coef, additional_freq, additional_phase]
    builder.play(i * 50e-9, "ch1", 0.5, "hann", 45e-9, 0, 0.5e-9)
    builder.play(i * 50e-9, "ch2", 0.3, "halfcos", 30e-9)
    # channel_name, phase
    # phase is in number of cycles. 0.1 means 0.1 * 2 * pi
    builder.shift_phase("ch1", 0.1)
    builder.shift_phase("ch2", -0.1)
req = builder.build()

client = PulseGenClient(port=5200)
result = client.run(req)

# result is a dictionary of channel_name -> (I array, Q array)
t1 = np.arange(0, 100000) / 2e-9
plt.plot(t1, result["ch1"][0])
plt.plot(t1, result["ch1"][1])
t2 = np.arange(0, 50000) / 1e-9
plt.plot(t2, result["ch2"][0])
plt.plot(t2, result["ch2"][1])
plt.show()
```

## Note

The server is still under active development. The API may change drastically in
the future.
