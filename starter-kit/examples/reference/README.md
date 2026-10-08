# Synthetic reference adapter example

All source, captures, revisions and verifier results here are **synthetic fixture data**. No AE/iPhone/browser or live agent run is claimed. The placeholder candidate SHA and module are not a product build. The self-authored policy is advisory, never a protected baseline. No trusted witness is supplied.

From repository root:

```sh
python3 starter-kit/scripts/check_reference_obligations.py starter-kit/examples/reference/ledger.json \
  --policy starter-kit/examples/reference/policy.json --evidence-root starter-kit/examples/reference
python3 starter-kit/scripts/reference_engineering.py compile starter-kit/examples/reference/observations.json \
  --evidence-root starter-kit/examples/reference
```

PASS here exercises consistency only. Generated scenarios remain NOT_RUN. For product use replace identity, observations, owner and typed verifier artifacts with actual project Evidence; independently approve the policy/witness and use the combined protected check. [Contract](../../../docs/REFERENCE_EVIDENCE_OBLIGATIONS_PROPOSAL.md).
