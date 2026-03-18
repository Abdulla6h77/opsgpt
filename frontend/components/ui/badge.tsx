import { cva, type VariantProps } from "class-variance-authority";
import { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold",
  {
    variants: {
      variant: {
        default: "border-border bg-accent text-accent-foreground",
        critical: "border-red-500/30 bg-red-500/15 text-red-300",
        high: "border-orange-500/30 bg-orange-500/15 text-orange-300",
        medium: "border-yellow-500/30 bg-yellow-500/15 text-yellow-300",
        low: "border-green-500/30 bg-green-500/15 text-green-300"
      }
    },
    defaultVariants: {
      variant: "default"
    }
  }
);

type BadgeProps = HTMLAttributes<HTMLDivElement> & VariantProps<typeof badgeVariants>;

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

