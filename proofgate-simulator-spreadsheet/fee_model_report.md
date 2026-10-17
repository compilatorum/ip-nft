#!/usr/bin/env node
"""airtable_fee_import.js

Importa os CSVs de fee simulation para Airtable.

Pré-requisitos:
  npm install airtable dotenv

Arquivo .env:
  AIRTABLE_API_KEY=key_xxx
  AIRTABLE_BASE_ID=appzXiVkuxVAOCDrt

Uso:
  node airtable_fee_import.js
"""

require('dotenv').config();
const fs = require('fs');
const parse = require('csv-parse/lib/sync');
const Airtable = require('airtable');

const base = new Airtable({ apiKey: process.env.AIRTABLE_API_KEY }).base(process.env.AIRTABLE_BASE_ID);

function readCsv(path) {
  const content = fs.readFileSync(path, 'utf8');
  return parse(content, { columns: true, skip_empty_lines: true, trim: true });
}

async function createRecords(tableName, rows) {
  const table = base(tableName);
  const batch = rows.map(r => ({ fields: r }));
  const page = await table.create(batch.slice(0, 10));
  console.log(`Inserted ${page.length} records into ${tableName}`);
  if (batch.length > 10) {
    const remaining = batch.slice(10);
    for (let i = 0; i < remaining.length; i += 10) {
      const chunk = remaining.slice(i, i + 10);
      await table.create(chunk);
    }
  }
}

(async () => {
  try {
    const detail = readCsv('./proofgate-simulator-spreadsheet/administrative_fee_simulation_detailed.csv');
    const normalized = detail.map(r => ({
      Model: r.Model,
      RatePct: Number(r.RatePct),
      RunID: r.RunID,
      Amount: Number(r.Amount),
      FeeAmount: Number(r.FeeAmount),
      EffectiveTradeAmount: Number(r.EffectiveTradeAmount),
      PassAfter: r.PassAfter === 'TRUE',
      VerdictBefore: r.VerdictBefore,
      VerdictAfter: r.VerdictAfter,
      RevenueCollected: Number(r.RevenueCollected),
    }));

    await createRecords('FeeSimulationRuns', normalized);
    console.log('Done.');
  } catch (err) {
    console.error('Airtable import failed:', err);
    process.exit(1);
  }
})();

