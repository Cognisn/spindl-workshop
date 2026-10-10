# Exercise 2: The Same Server, Spooled (50 to 65 min mark)

Change `naive` to `spindl` in your client config and restart the client.
Confirm the `fw_spooler_*` tools now appear. Nothing else changed: same
data file, same three firewall tools, one constructor argument different.

## Task 0: Same question, different physics

Ask exactly the same as Exercise 1 Task 1: *"Which enabled rules allow RDP
(tcp/3389) from the internet, meaning source zone untrust with an any or
0.0.0.0/0 source?"*

Watch the shape change: `fw_get_rulebase` now returns a **summary** with a
`spool_id`, record count, columns, and sample rows, a few hundred tokens
instead of ~127,000. The model then drives `fw_spooler_query` with filters
to pull only matching rules.

## Task 1: Aggregate instead of dump

Ask: *"Which source IP generated the most denies in the last 24 hours?"*

The model should call `fw_get_traffic_logs`, receive a spool summary, then
use `fw_spooler_aggregate` grouped by `source_ip` filtered to denies. One
noisy address should stand out dramatically.

## Task 2: Pull the thread

You have found a noisy scanner. Now investigate like it is an incident:

- *"Did that scanner ever succeed in connecting? Show any allowed sessions."*
- *"Which rule permitted those sessions, and what do we know about it?"*
- *"What services has that scanner probed, and how often?"* (watch for
  `fw_spooler_distinct` on the service column, filtered to the scanner's
  source IP; the response echoes the filters it applied)

Note that the entire investigation happens without a single bulk dump
entering your context.

## Task 3: The skills guide (demonstrated from the front)

Ask: *"What tools does this firewall server offer, and how should I use the
rulebase tool?"* The model calls `fw_list_tools` and `fw_describe_tool`,
retrieving usage guides on demand with all cross-references resolved to
prefixed names. Tool descriptions stay lean; depth is fetched only when
needed.

## Task 4: Compare your notes

Same questions, same data. Compare context consumption, answer accuracy, and
the number of questions you could afford to keep asking.
