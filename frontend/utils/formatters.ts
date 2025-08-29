/**
 * Format a number as Indonesian Rupiah currency
 * @param value - The number to format
 * @returns Formatted currency string with Rp prefix
 */
export const formatCurrency = (value: number): string => {
  return `Rp${value.toLocaleString('id-ID')}`
} 