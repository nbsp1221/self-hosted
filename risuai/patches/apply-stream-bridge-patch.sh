#!/bin/sh
set -eu

PATCH_FILE="/tmp/api-v3-messageport-stream-bridge.patch"
FACTORY_FILE="src/ts/plugins/apiV3/factory.ts"
V3_FILE="src/ts/plugins/apiV3/v3.svelte.ts"

if grep -q "replaceStreamsWithPorts" "$FACTORY_FILE" \
  && grep -q "STREAM_PORT" "$FACTORY_FILE" \
  && grep -q "Compatibility marker for plugins" "$FACTORY_FILE" \
  && grep -q "ReadableStream<string>" "$V3_FILE"; then
  echo "RisuAI API v3 stream bridge patch already present; skipping."
  exit 0
fi

git apply --check "$PATCH_FILE"
git apply "$PATCH_FILE"

grep -q "replaceStreamsWithPorts" "$FACTORY_FILE"
grep -q "reconstructStreamsFromPorts" "$FACTORY_FILE"
grep -q "STREAM_PORT" "$FACTORY_FILE"
grep -q "Compatibility marker for plugins" "$FACTORY_FILE"
grep -q "ReadableStream<string>" "$V3_FILE"
