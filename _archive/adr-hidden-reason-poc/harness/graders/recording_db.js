export const opened = [];

export function openDatabase(path, options = {}) {
  opened.push({ path, readOnly: Boolean(options) && options.readOnly === true });
  const statement = { all: () => [], get: () => undefined, run: () => ({ changes: 0 }) };
  return { prepare: () => statement, exec: () => {}, close: () => {}, [Symbol.dispose]: () => {} };
}
