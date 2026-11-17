#!/bin/sh
# Computes expected.json, the digest test vectors, from spec/0.7/bundle-format.md §7.6 alone.
#
# Independent of scs_validator: each YAML document under workspace/ and variants/ was
# transcribed by hand to JSON under canonical/ (dates and timestamps written as §7.6 says);
# jq -cS gives the canonical form and shasum the hash. test_digest_vectors.py checks the
# implementation against the result. Re-run only when a vector changes, and review the diff.
set -eu
cd "$(dirname "$0")"

doc() { printf 'sha256:%s' "$(jq -cSj . "canonical/$1.json" | shasum -a 256 | cut -d' ' -f1)"; }
arr() { printf 'sha256:%s' "$(printf '%s' "$1" | jq -cSj . | shasum -a 256 | cut -d' ' -f1)"; }

alpha=$(doc alpha)
alpha_changed=$(doc alpha-changed)
beta=$(doc beta)
gamma=$(doc gamma)
first_m=$(doc first)
second_m=$(doc second)
proj_m=$(doc project-bundle)

# [manifest digest, [[SCD id, digest]...] sorted by id, [[import ref, content digest]...] sorted by ref]
first=$(arr "[\"$first_m\",[[\"scd:project:alpha\",\"$alpha\"],[\"scd:project:gamma\",\"$gamma\"]],[]]")
first_changed=$(arr "[\"$first_m\",[[\"scd:project:alpha\",\"$alpha_changed\"],[\"scd:project:gamma\",\"$gamma\"]],[]]")
second=$(arr "[\"$second_m\",[[\"scd:project:beta\",\"$beta\"]],[]]")
proj=$(arr "[\"$proj_m\",[],[[\"bundle:first:1.0.0\",\"$first\"],[\"bundle:second:1.0.0\",\"$second\"]]]")
proj_changed=$(arr "[\"$proj_m\",[],[[\"bundle:first:1.0.0\",\"$first_changed\"],[\"bundle:second:1.0.0\",\"$second\"]]]")

jq -n --arg alpha "$alpha" --arg alpha_changed "$alpha_changed" --arg beta "$beta" \
  --arg gamma "$gamma" --arg first_m "$first_m" --arg second_m "$second_m" --arg proj_m "$proj_m" \
  --arg first "$first" --arg first_changed "$first_changed" --arg second "$second" \
  --arg proj "$proj" --arg proj_changed "$proj_changed" '{
    documents: {alpha: $alpha, "alpha-changed": $alpha_changed, beta: $beta, gamma: $gamma,
                first: $first_m, second: $second_m, "project-bundle": $proj_m},
    content: {first: $first, second: $second, "project-bundle": $proj},
    content_with_alpha_changed: {first: $first_changed, second: $second,
                                 "project-bundle": $proj_changed}
  }' > expected.json
