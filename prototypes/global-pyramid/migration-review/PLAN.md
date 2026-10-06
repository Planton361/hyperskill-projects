# Exact spatial migration review plan

1. Record protected bytes and inspect existing exact-preview, schema, packaging and transaction contracts.
2. Freeze a new deterministic, non-overwriting review package: existing preview bytes, self-contained comparison view, explicit source/history bindings and exact candidate State/Production bytes. No layout generation.
3. Validate package integrity and source freshness independently. Require an external human-copied manifest fingerprint; approval creates only a bound seal, never publishes real state.
4. Implement an explicitly marked disposable-only publication adapter using the existing exclusive lock, durable staging/journal/swaps/recovery and post-swap exact byte verification.
5. Test stale/rehash attacks, strict persisted global authority, semantics/history/generation, idempotence, reserved-slot reveals/promotion, exceptions and hard crashes. Smoke-test exact review and disposable Production in the browser.
6. Verify protected bytes again and document results, remaining limitations and one recommendation. No real approval token is supplied by the agent; seals/apply in this task are test-fixture only.
