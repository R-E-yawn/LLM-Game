/**
 * Formats message text by converting markdown to HTML
 * - Converts **text** to <strong>text</strong>
 * - Adds line breaks after numbered list items
 * - Preserves other formatting
 */
export function formatMessage(text) {
  if (!text) return '';

  let formatted = text;

  // First, convert **bold** to <strong>bold</strong>
  // Handle multiple bold sections
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

  // Format numbered lists - split items and add proper spacing
  // Pattern: "1. **text**: description 2. **text**: description"
  // Should become: "1. **text**: description<br /><br />2. **text**: description"
  
  // Split by numbered list pattern (number followed by period and space)
  // This regex finds: number, period, space, then everything until next number or end
  formatted = formatted.replace(/(\d+\.\s+[^0-9]+?)(?=\s*\d+\.|$)/g, (match) => {
    const trimmed = match.trim();
    // If it doesn't already end with a break, add double break for spacing
    if (!trimmed.endsWith('<br />') && !trimmed.endsWith('<br>') && trimmed.length > 0) {
      return trimmed + '<br /><br />';
    }
    return match;
  });

  // Handle cases where there's text before the first numbered item
  // Add a break before the first numbered list if needed
  formatted = formatted.replace(/([^<])(\d+\.\s+)/g, (match, before, listStart) => {
    // If the text before doesn't end with a break, add one
    if (!before.endsWith('<br />') && !before.endsWith('<br>') && before.trim().length > 0) {
      return before + '<br /><br />' + listStart;
    }
    return match;
  });

  // Clean up multiple consecutive breaks (more than 2)
  formatted = formatted.replace(/(<br \/>\s*){3,}/g, '<br /><br />');

  // Clean up any trailing breaks
  formatted = formatted.replace(/(<br \/>\s*)+$/, '');

  return formatted;
}

