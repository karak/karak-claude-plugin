/*
 * Button.stories.tsx — example-stack story template (CSF3).
 *
 * Norms shown (references/catalog-norms.md):
 *  - title = atomic path "Atoms/Button" -> stable story IDs "atoms-button--primary"
 *    that E2E/visual checks target via iframe.html?id=... (treat IDs as a contract)
 *  - one named story per design comp / state
 *  - argTypes documents the full CATALOG prop API (the token-bound enums) so
 *    Storybook Docs reads as the spec. Native HTML passthrough attributes
 *    (onClick, type, aria-*) are intentionally left undocumented — only the
 *    catalog-specific props are specced.
 */
import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "./Button";

const meta: Meta<typeof Button> = {
  title: "Atoms/Button",
  component: Button,
  // argTypes = designer-readable prop spec. Every prop appears with a control,
  // a description, and its type/default; a prop missing here is invisible to
  // reviewers, so treat this block as part of the component's public definition.
  argTypes: {
    variant: {
      control: "inline-radio",
      options: ["primary", "secondary"],
      description: "Visual emphasis. Maps 1:1 to the Figma `variant` property.",
      table: { type: { summary: "primary | secondary" }, defaultValue: { summary: "primary" } },
    },
    size: {
      control: "inline-radio",
      options: ["md", "sm"],
      description: "Control height. `md` keeps the 44px min touch target.",
      table: { type: { summary: "md | sm" }, defaultValue: { summary: "md" } },
    },
    disabled: {
      control: "boolean",
      description: "Native disabled state (dims + blocks pointer events).",
      table: { type: { summary: "boolean" }, defaultValue: { summary: "false" } },
    },
    children: { control: "text", description: "Label text." },
  },
  args: { children: "Button" },
};
export default meta;

type Story = StoryObj<typeof Button>;

// One story per design comp / state — not one component per state.
export const Primary: Story = { args: { variant: "primary" } };
export const Secondary: Story = { args: { variant: "secondary" } };
export const Small: Story = { args: { size: "sm" } };
export const Disabled: Story = { args: { disabled: true } };
