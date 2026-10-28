/**
 * Currency, Number, and Date Formatters
 * Uses standard Indian Rupee (INR) formatting where applicable.
 */

export function formatINR(value: number | null | undefined, fallback = '—'): string {
  if (value === null || value === undefined || isNaN(value)) {
    return fallback;
  }
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatCompactINR(value: number | null | undefined, fallback = '—'): string {
  if (value === null || value === undefined || isNaN(value)) {
    return fallback;
  }
  if (Math.abs(value) >= 10000000) {
    return `₹${(value / 10000000).toFixed(2)} Cr`;
  }
  if (Math.abs(value) >= 100000) {
    return `₹${(value / 100000).toFixed(2)} Lakh`;
  }
  return formatINR(value, fallback);
}

export function formatPercent(value: number | null | undefined, fallback = '—'): string {
  if (value === null || value === undefined || isNaN(value)) {
    return fallback;
  }
  return `${value.toFixed(1)}%`;
}

export function formatDate(dateString: string | null | undefined, fallback = '—'): string {
  if (!dateString) return fallback;
  try {
    const d = new Date(dateString);
    if (isNaN(d.getTime())) return fallback;
    return new Intl.DateTimeFormat('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    }).format(d);
  } catch {
    return fallback;
  }
}

export function formatDateTime(dateString: string | null | undefined, fallback = '—'): string {
  if (!dateString) return fallback;
  try {
    const d = new Date(dateString);
    if (isNaN(d.getTime())) return fallback;
    return new Intl.DateTimeFormat('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(d);
  } catch {
    return fallback;
  }
}

export function parseAssumptions(assumptionsJson: string | null | undefined): string[] {
  if (!assumptionsJson) return [];
  try {
    const parsed = JSON.parse(assumptionsJson);
    if (Array.isArray(parsed)) return parsed;
    return [String(parsed)];
  } catch {
    return [assumptionsJson];
  }
}
