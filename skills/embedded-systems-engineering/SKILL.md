---
name: embedded-systems-engineering
description: Embedded and hardware-adjacent engineering for firmware on microcontrollers, sensor and actuator interfaces, and board-level integration - handle hard real-time timing, interrupts and concurrency, memory and power budgets, fault-tolerant safe states, and hardware-in-the-loop verification. Use when writing or reviewing firmware, drivers, control loops, or code that must interact correctly with physical signals.
license: MIT
metadata:
  author: sahildark789
  version: "1.0.0"
---

# Embedded Systems Engineering

Embedded code runs against physics: time keeps passing, memory is fixed, power is finite,
and sensors lie. Design for those constraints before writing the first driver.

## 1. Write the hardware constraints down

Before coding, record from the datasheets and the board schematic:

- Clock sources and frequencies; timer resolution and jitter.
- Memory: flash and RAM sizes, stack limits, and any external memory timing.
- Peripherals and their pins, voltage levels, and shared buses (I2C addresses, SPI chip selects).
- Power: active and sleep current per mode; battery or supply limits.
- Electrical limits: absolute maximum ratings, pull-up requirements, debounce, EMI exposure.
- Sensor specs: range, resolution, noise density, sample rate, settling time, and failure signals.

## 2. Design the timing model

- Classify each task as hard real-time (missing a deadline is a fault), firm, or soft.
- Prefer a fixed-period control loop driven by a timer over `delay()`-style busy waiting.
- Keep interrupt service routines short: set a flag or push to a queue, then do the work in a task or main loop.
- Compute worst-case execution time for each deadline-critical path and check it against the period.
- Use a monotonic clock source for timeouts; do not rely on counting loop iterations.

## 3. Handle concurrency safely

- Protect data shared between an ISR and the main context with atomic access or a
  critical section kept as short as possible.
- Mark variables touched in ISRs as `volatile` where the compiler could otherwise cache them,
  and remember that `volatile` alone is not thread-safe.
- Avoid dynamic allocation in steady-state code paths. Allocate at startup and check the results.
- Audit stack depth: measure high-water marks under the worst-case call chain.

## 4. Treat sensors and actuators as unreliable

- Validate every reading: range check, plausibility check against the previous value, and
  stale-data detection by timestamp.
- Filter with a method matched to the signal (median for spikes, low-pass for noise), and document the cutoff.
- Debounce mechanical inputs in time, not in loop counts.
- Before driving an output, check the safe-state conditions. Never drive an actuator from an unvalidated input.

## 5. Define the safe state

- For each actuator, state the output when power, communication, or sensing is lost.
- Use a watchdog timer, and feed it only from code that proves the system is making progress
  (not from an unconditional loop in the idle task).
- Log faults in non-volatile memory with enough context to diagnose them after a reset.
- Test brown-out and reset behavior explicitly.

## 6. Budget power

- Measure current in each mode, not just the datasheet typical value.
- Sleep whenever idle; wake on interrupt, not on polling.
- Account for peripheral and radio bursts in the average and peak budget.

## 7. Verify with the hardware

- Unit-test pure logic on the host with the hardware layer mocked.
- Use hardware-in-the-loop tests for timing, interrupts, and drivers, with a logic analyzer or oscilloscope.
- Test with the sensor disconnected, shorted, and out of range.
- Run long soak tests to surface memory leaks, drift, and thermal effects.
- Verify on the production board revision, not only on the development kit.

## Checklist

- [ ] Hardware constraints recorded from datasheets and schematic.
- [ ] Deadlines classified; worst-case timing measured on target.
- [ ] ISR work is minimal; shared data is protected.
- [ ] Every sensor input is validated and has a stale-data path.
- [ ] Safe state, watchdog, and fault logging are defined and tested.
- [ ] Power measured per mode against the budget.

## Anti-patterns

- Busy-wait delays inside control loops.
- Blocking calls or `printf` inside an ISR.
- Trusting a sensor value with no range or staleness check.
- Testing only on the development kit and shipping a different board revision.
