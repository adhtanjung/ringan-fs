# UI Consistency Guide

This document outlines the UI principles and patterns established for the Ringan mental health chat application using shadcn/vue components.

## Core Design Principles

### 1. Component-First Approach
- **Use shadcn/vue components** as the foundation for all UI elements
- **Avoid custom CSS** for common UI patterns
- **Leverage component variants** for different states and contexts

### 2. Consistent Color System
- **Sentiment Analysis Colors:**
  - Positive: `default` variant (green)
  - Negative: `destructive` variant (red)
  - Neutral: `secondary` variant (gray)
  - Unknown: `outline` variant

- **Crisis Risk Colors:**
  - High: `destructive` variant (red)
  - Medium: `default` variant (yellow/orange)
  - Low: `secondary` variant (green)
  - Unknown: `outline` variant

### 3. Interactive Elements
- **Tooltips** for all interactive elements to provide context
- **Consistent button sizes** using shadcn/vue size variants
- **Hover states** handled by component variants

## Component Usage Patterns

### Badge Component
```vue
<!-- Sentiment indicators -->
<Badge :variant="getSentimentBadgeVariant(sentiment)">
  {{ getSentimentText(sentiment) }}
</Badge>

<!-- Crisis risk indicators -->
<Badge :variant="getCrisisRiskBadgeVariant(risk)">
  {{ risk }}
</Badge>

<!-- Status indicators -->
<Badge variant="outline" class="text-xs">
  {{ timestamp }}
</Badge>
```

### Progress Component
```vue
<!-- Confidence indicators -->
<Progress
  :value="confidence * 100"
  class="w-12 h-1"
/>
```

### Tooltip Component
```vue
<!-- Interactive elements with context -->
<TooltipProvider>
  <Tooltip>
    <TooltipTrigger as-child>
      <Button variant="ghost" size="sm">
        <Icon />
      </Button>
    </TooltipTrigger>
    <TooltipContent>
      <p>Action description</p>
    </TooltipContent>
  </Tooltip>
</TooltipProvider>
```

### Button Component
```vue
<!-- Consistent button patterns -->
<Button
  variant="ghost"
  size="sm"
  class="h-7 w-7 p-0 rounded-full"
>
  <Icon class="w-3 h-3" />
</Button>
```

## Message Bubble Specific Patterns

### Sentiment Analysis Display
1. **Primary indicators** use Badge components with semantic variants
2. **Detailed information** shown in Tooltip on hover
3. **Confidence levels** displayed with Progress component
4. **Crisis indicators** use appropriate Badge variants

### Action Buttons
1. **All interactive elements** wrapped in TooltipProvider
2. **Consistent sizing** using shadcn/vue size variants
3. **Semantic variants** for different action types

### Error States
1. **Error messages** displayed as Badge with `destructive` variant
2. **Consistent styling** across all error states

## Implementation Guidelines

### 1. Type Safety
- Always properly type component props
- Use union types for variant props
- Leverage TypeScript for component interfaces

### 2. Accessibility
- Use semantic HTML elements
- Provide proper ARIA labels
- Ensure keyboard navigation support

### 3. Responsive Design
- Use Tailwind CSS responsive utilities
- Test on multiple screen sizes
- Maintain component consistency across breakpoints

### 4. Dark Mode Support
- Leverage shadcn/vue's built-in dark mode support
- Test all components in both light and dark themes
- Ensure proper contrast ratios

## File Structure
```
components/
├── ui/                    # shadcn/vue components
│   ├── badge/
│   ├── button/
│   ├── progress/
│   ├── tooltip/
│   └── ...
├── animations/            # Custom animated components
│   ├── MessageBubble.vue  # Polished with shadcn/vue
│   └── ...
└── ...
```

## Best Practices

1. **Import only what you need** from shadcn/vue components
2. **Use component variants** instead of custom CSS classes
3. **Provide meaningful tooltips** for all interactive elements
4. **Test components** in both light and dark modes
5. **Maintain consistent spacing** using Tailwind utilities
6. **Use semantic color variants** for different states

## Migration Checklist

When updating existing components to follow these principles:

- [ ] Replace custom UI elements with shadcn/vue components
- [ ] Add proper TypeScript types for all props
- [ ] Implement tooltips for interactive elements
- [ ] Use semantic color variants
- [ ] Test in both light and dark modes
- [ ] Ensure accessibility compliance
- [ ] Update documentation

## Examples

### Before (Custom Implementation)
```vue
<div class="custom-sentiment-indicator">
  <div class="sentiment-dot bg-green-500"></div>
  <span class="sentiment-text">Positive</span>
</div>
```

### After (shadcn/vue Implementation)
```vue
<Badge variant="default" class="text-xs">
  Positive
</Badge>
```

This approach provides:
- Better consistency
- Improved accessibility
- Easier maintenance
- Better TypeScript support
- Built-in dark mode support
