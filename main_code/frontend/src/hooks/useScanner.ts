/**
 * useScanner — Barcode Scanner Integration Hook.
 *
 * Maintains a hidden input that stays permanently focused to capture
 * barcode scanner input (which behaves like keyboard typing + Enter).
 * Automatically re-focuses after clicks or window switches.
 */

import { useState, useEffect, useRef, useCallback } from "react";

export function useScanner(onScan: (value: string) => void) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [value, setValue] = useState("");

  useEffect(() => {
    const focusInput = () => {
      inputRef.current?.focus();
    };

    // Force initial focus
    focusInput();

    // Re-focus when user clicks elsewhere in the page
    window.addEventListener("click", focusInput);
    // Re-focus when the browser window regains focus (e.g. alt-tab back)
    window.addEventListener("focus", focusInput);

    return () => {
      window.removeEventListener("click", focusInput);
      window.removeEventListener("focus", focusInput);
    };
  }, []);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "Enter") {
        const trimmed = value.trim();
        if (trimmed) {
          onScan(trimmed);
          setValue("");
        }
      }
    },
    [value, onScan]
  );

  return {
    inputRef,
    value,
    setValue,
    handleKeyDown,
  } as const;
}
