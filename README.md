# Master's degree thesis

In this repository there are the files for my master's degree thesis on automated acceptance testing of embedded IoT devices. You can find the final document
(in Italian) [here](https://github.com/alerighi/masters-degree-thesis-doc/blob/master/tesi.pdf).

## Description

This software implements an automated system for automated performing acceptance tests (i.e. tests done before deploying
the firmware to thousands of devices) on embedded devices, in particular I took as a case study a Wi-Fi electric radiator from IRSAP s.p.a. of which I wrote the firmware while working in IOTINGA.

This system does test the firmware while considering it a black-box, and it does so by testing it on the real hardware.
To do so a test fixture was built.

<img src="img/fixture.png" alt="text fixture">

It consists in the connection between a devkit of the device and a Raspberry Pi, that runs the test software. Tests
are written with `pytest` with a custom fixture that passes a contexts that allows interacting with the device, both
locally and trough the cloud:

- control inputs (GPIO) of the device
- read the status of outputs (GPIO) of the device
- send a message to the device trough the cloud
- receive a message from the device trough the cloud
- call a local local REST API on the device
- write serial commands to the device
- read serial logs from the device

The Raspberry Pi also acts as a Wi-Fi AP and client trough the integrated Wi-Fi interface. This allows the connection
to the device as the mobile app would do, but also the test of different AP configurations and the introduction
of network errors, to check if the device behaves correctly (what if the connection goes down, then back up again, what
if some packets gets lost, what if the DNS doesn't work but internet does, etc).

## Installation

This software requires python 3.11. Once installed, create a virtual environment, then just run:

```bash
pip install -e .
```

to install the software in development mode.

Everything that is needed is in the `pyproject.toml` file, that specifies all the project dependencies and stuff.