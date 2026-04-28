/**
 * TrafficLightBanner — High-visibility status banner.
 *
 * Displays a large, color-coded (green/red) banner with an icon,
 * title, prominent text, and optional subtitle. Designed for
 * industrial environments where visual clarity is critical.
 */

import { CheckCircle2, AlertTriangle } from "lucide-react";

interface TrafficLightBannerProps {
  variant: "success" | "error";
  title: string;
  massiveText: string;
  subtitle?: string;
}

/** CSS class sets per variant for container styling. */
const VARIANT_CLASSES: Record<TrafficLightBannerProps["variant"], string> = {
  success:
    "bg-industrial-success border-industrial-success border-4 text-white",
  error: "bg-industrial-danger border-industrial-danger border-4 text-white",
};

/** Icon components per variant. */
const VARIANT_ICONS: Record<
  TrafficLightBannerProps["variant"],
  typeof CheckCircle2
> = {
  success: CheckCircle2,
  error: AlertTriangle,
};

export const TrafficLightBanner = ({
  variant,
  title,
  massiveText,
  subtitle,
}: TrafficLightBannerProps) => {
  const Icon = VARIANT_ICONS[variant];

  return (
    <div
      id={`banner-${variant}`}
      className={`w-full p-8 rounded-2xl flex flex-col items-center justify-center text-center transition-all duration-300 ${VARIANT_CLASSES[variant]}`}
      role="status"
      aria-live="polite"
    >
      <div className="text-3xl mb-4 opacity-90 flex items-center justify-center gap-3">
        <Icon size={40} aria-hidden="true" />
        {title}
      </div>
      <h2 className="text-[5rem] font-black leading-tight m-0 tracking-tight">
        {massiveText}
      </h2>
      {subtitle && (
        <p className="text-3xl mt-4 m-0 font-medium opacity-90">{subtitle}</p>
      )}
    </div>
  );
};
