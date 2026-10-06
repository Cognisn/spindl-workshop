# Exercise 1: The Naive Server (15 to 25 min mark)

Server mode: `--mode naive`. Confirm your client shows tools prefixed `fw_`
and that `fw_spooler_*` tools are **absent**.

Before each task, note your client's context/token usage indicator.

## Task 0: Connectivity check

Ask: *"What firewall device am I connected to?"*

Expected: a small `fw_get_device_info` call. Hostname `fw-edge-01`.

## Task 1: The rulebase dump

Ask: *"Which enabled rules allow RDP (tcp/3389) from the internet, meaning
source zone untrust with an any or 0.0.0.0/0 source?"*

Watch what happens: the model calls `fw_get_rulebase` and the **entire
1,200 rule policy (~127k tokens)** lands in context. Note:

- how long the response takes
- your context usage after the call
- whether the model finds the correct rule, or truncates and guesses

## Task 2: The log dump

Ask: *"Which source IP generated the most denies in the last 24 hours?"*

The model calls `fw_get_traffic_logs`. Unfiltered, that is **~160k tokens** of
log entries. Depending on your client this may exceed the context window
outright, be truncated silently, or evict earlier conversation.

## Task 3: Reflect

- Did the model answer both questions correctly?
- How much of your context window is now consumed?
- What would question three cost you?

Keep your notes. You will repeat the identical questions in Exercise 2.
