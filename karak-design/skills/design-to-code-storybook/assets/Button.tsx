/*
 * Button.tsx — example-stack component template (React / Tailwind + cva).
 *
 * Shadcn/ui components ARE this pattern (a cva-styled element over Tailwind);
 * this template follows that idiom rather than importing a specific primitive,
 * so it drops cleanly into a shadcn or a plain-Tailwind project alike.
 *
 * Demonstrates the catalog norms (references/catalog-norms.md):
 *  - token-bound ENUM props only; no raw color/size/style pass-through
 *  - every visual property reads a SEMANTIC token (via Tailwind arbitrary
 *    values bound to CSS vars), never a primitive or a raw value
 *  - a new prop's default reproduces current behavior (backward-compatible)
 *
 * Colocate with Button.stories.tsx and Button.spec.ts in the same folder.
 * Adapt syntax to the host stack; keep the rules. See assets/stack-adaptation.md.
 */
import { cva, type VariantProps } from "class-variance-authority";

// Each axis is a discrete enum mapping to semantic tokens — the same axes the
// Figma variant and the argTypes control expose (the 1:1 that lets Code Connect
// map them). Every value here reads a semantic token; nothing is a raw hex/px.
const button = cva(
  // `disabled:opacity-50` is a fixed interaction affordance (a uniform dim for the
  // disabled state), not a themed color, so it is intentionally not tokenized —
  // same exception as `transparent` below. Tokenize it (--control-disabled-opacity)
  // only if a design actually varies disabled dimming per theme.
  "inline-flex items-center justify-center rounded-[var(--control-radius)] " +
    "px-[var(--control-pad-x)] py-[var(--control-pad-y)] " +
    "transition-colors disabled:opacity-50 disabled:pointer-events-none",
  {
    variants: {
      variant: {
        primary: "bg-[var(--color-accent)] text-[var(--label-on-accent)]",
        secondary:
          // `transparent` is a keyword, not a themed color, so it is not tokenized.
          "bg-transparent text-[var(--color-accent)] " +
          "border border-[var(--color-accent)]",
      },
      // Height and font-size are token-bound too (not Tailwind's fixed h-11/text-base
      // scale), so control geometry themes with everything else. The md tokens
      // carry the 44px min touch target.
      size: {
        md: "h-[var(--control-height-md)] text-[length:var(--font-control-md)]",
        sm: "h-[var(--control-height-sm)] text-[length:var(--font-control-sm)]",
      },
    },
    // Defaults reproduce the original single-variant rendering.
    defaultVariants: { variant: "primary", size: "md" },
  },
);

// Omit `className` and `style`: exposing them would be the raw-styling escape
// hatch catalog-norms.md#props forbids, and a spread `className` would also
// clobber the cva output. The prop API is exactly the token-bound enums + native
// button behavior (onClick, type, disabled, ...).
type ButtonProps = Omit<
  React.ButtonHTMLAttributes<HTMLButtonElement>,
  "className" | "style"
> &
  VariantProps<typeof button>;

export function Button({ variant, size, ...props }: ButtonProps) {
  return <button className={button({ variant, size })} {...props} />;
}
