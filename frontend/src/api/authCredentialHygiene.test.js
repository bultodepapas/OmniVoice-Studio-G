import { describe, expect, it } from 'vitest';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const SRC = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SOURCE_EXTENSIONS = new Set(['.js', '.jsx', '.ts', '.tsx']);

function* productionFiles(directory) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      if (entry.name === 'test') continue;
      yield* productionFiles(absolute);
      continue;
    }
    if (SOURCE_EXTENSIONS.has(path.extname(entry.name)) && !/\.test\.[jt]sx?$/.test(entry.name)) {
      yield absolute;
    }
  }
}

const sources = () =>
  [...productionFiles(SRC)].map((file) => ({
    file: path.relative(SRC, file).replaceAll('\\', '/'),
    source: fs.readFileSync(file, 'utf8'),
  }));

describe('administrator credential hygiene static guard', () => {
  it('has no production path that durably writes the legacy master key', () => {
    const violations = sources()
      .filter(({ source }) =>
        /localStorage\.setItem\(\s*(?:LS_API_KEY|LEGACY_API_KEY_STORAGE_KEY|['"]ov_api_key['"])/.test(
          source,
        ),
      )
      .map(({ file }) => file);

    expect(violations, 'OMNIVOICE_API_KEY must never enter localStorage').toEqual([]);
  });

  it('has no production WebSocket query builder for a master API key', () => {
    const forbidden = [
      /searchParams\.set\(\s*['"]api_key['"]/,
      /[?&]api_key=\$\{/,
      /[?&]api_key=['"]\s*\+/,
    ];
    const violations = sources()
      .filter(({ source }) => forbidden.some((pattern) => pattern.test(source)))
      .map(({ file }) => file);

    expect(violations, 'WebSocket URLs may contain ws_ticket, never a master key').toEqual([]);
  });

  it('keeps both WebSocket consumers behind the authenticated URL boundary', () => {
    const constructors = sources()
      .filter(({ source }) => source.includes('new WebSocket('))
      .map(({ file, source }) => ({ file, authenticated: source.includes('authenticatedWsUrl') }));

    expect(constructors).toEqual([
      { file: 'components/CaptureWidget.jsx', authenticated: true },
      { file: 'hooks/useRealtimeEvents.js', authenticated: true },
    ]);
  });
});
