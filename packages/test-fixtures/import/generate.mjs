#!/usr/bin/env node

import { createHash } from "node:crypto";
import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const args = process.argv.slice(2);
const outIndex = args.indexOf("--out");
const outDir = resolve(
  outIndex >= 0 && args[outIndex + 1]
    ? args[outIndex + 1]
    : "packages/test-fixtures/import/generated",
);

mkdirSync(outDir, { recursive: true });

const header = [
  "source_reference",
  "reported_at",
  "project_code",
  "location_code",
  "service_code",
  "issue_code",
  "sentiment",
  "operational_severity",
  "content_masked",
];

const issues = ["ELV-01", "ELV-02", "ELV-06"];
const sentiments = ["NEGATIVE", "NEUTRAL", "POSITIVE", "UNKNOWN"];
const severities = ["SEV-2", "SEV-3", "SEV-4"];

function csvCell(value) {
  const text = String(value);
  return /[",\n\r]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function timestamp(index) {
  const day = 10 + (index % 7);
  const hour = String(index % 24).padStart(2, "0");
  const minute = String((index * 7) % 60).padStart(2, "0");
  return `2026-08-${String(day).padStart(2, "0")}T${hour}:${minute}:00+07:00`;
}

function validRow(prefix, index, overrides = {}) {
  const serial = String(index).padStart(6, "0");
  return {
    source_reference: `${prefix}-${serial}`,
    reported_at: timestamp(index),
    project_code: "PILOT_PROJECT",
    location_code: "S2",
    service_code: "SVC-17",
    issue_code: issues[index % issues.length],
    sentiment: sentiments[index % sentiments.length],
    operational_severity: severities[index % severities.length],
    content_masked: `Synthetic masked feedback ${prefix}-${serial}`,
    ...overrides,
  };
}

function writeText(name, text, expected) {
  const normalized = text.endsWith("\n") ? text : `${text}\n`;
  writeFileSync(resolve(outDir, name), normalized, "utf8");
  return {
    sha256: createHash("sha256").update(normalized).digest("hex"),
    bytes: Buffer.byteLength(normalized),
    expected,
  };
}

function writeCsv(name, rows, expected) {
  const body = [
    header.join(","),
    ...rows.map((row) => header.map((field) => csvCell(row[field])).join(",")),
  ].join("\n");
  return writeText(name, body, expected);
}

const generated = {};

const happy100 = Array.from({ length: 100 }, (_, index) =>
  validRow("HAPPY", index + 1),
);
generated["happy-100.csv"] = writeCsv("happy-100.csv", happy100, {
  total: 100,
  valid: 100,
  invalid: 0,
  duplicate: 0,
});

const mixedValid = Array.from({ length: 80 }, (_, index) =>
  validRow("MIXED", index + 1),
);
const mixedInvalidTimestamp = Array.from({ length: 5 }, (_, index) =>
  validRow("BAD-TIME", index + 1, { reported_at: "not-a-timestamp" }),
);
const mixedInvalidMapping = Array.from({ length: 5 }, (_, index) =>
  validRow("BAD-MAP", index + 1, { issue_code: "PKG-01" }),
);
const mixedDuplicates = mixedValid.slice(0, 10).map((row) => ({
  ...row,
  content_masked: `${row.content_masked} duplicate occurrence`,
}));
generated["mixed-80-10-10.csv"] = writeCsv(
  "mixed-80-10-10.csv",
  [...mixedValid, ...mixedInvalidTimestamp, ...mixedInvalidMapping, ...mixedDuplicates],
  { total: 100, valid: 80, invalid: 10, duplicate: 10 },
);

generated["duplicate-existing.csv"] = writeCsv(
  "duplicate-existing.csv",
  happy100.slice(0, 5),
  {
    total: 5,
    valid: 0,
    invalid: 0,
    duplicate: 5,
    precondition: "happy-100.csv has already reached COMPLETED",
  },
);

const boundary10000 = Array.from({ length: 10_000 }, (_, index) =>
  validRow("BOUNDARY", index + 1),
);
generated["boundary-10000.csv"] = writeCsv(
  "boundary-10000.csv",
  boundary10000,
  { total: 10_000, valid: 10_000, invalid: 0, duplicate: 0 },
);

const analyticsLines = Array.from({ length: 100_000 }, (_, index) => {
  const number = index + 1;
  return JSON.stringify({
    fixture_id: `PERF-${String(number).padStart(6, "0")}`,
    reported_at: timestamp(number),
    project_code: "PILOT_PROJECT",
    location_code: "S2",
    service_code: "SVC-17",
    issue_code: issues[number % issues.length],
    sentiment: sentiments[number % sentiments.length],
    operational_severity: severities[number % severities.length],
    decision_source: "SOURCE_TRUSTED",
    import_job_state: "COMPLETED",
  });
}).join("\n");
generated["analytics-100000.ndjson"] = writeText(
  "analytics-100000.ndjson",
  analyticsLines,
  { eligible_items: 100_000 },
);

writeFileSync(
  resolve(outDir, "manifest.generated.json"),
  `${JSON.stringify(
    {
      contract_version: "trusted-feedback-csv/v1",
      generator_version: "1.0.0",
      generated,
    },
    null,
    2,
  )}\n`,
  "utf8",
);

process.stdout.write(`${JSON.stringify(generated, null, 2)}\n`);
