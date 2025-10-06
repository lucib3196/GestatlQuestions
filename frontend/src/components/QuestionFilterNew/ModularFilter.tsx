import { useState } from "react"

export type Flag = {
  key: string
  label: string
  type?: "checkbox" | "toggle" | "select"
  options?: string[]
}

type FilterProps = {
  flags: Flag[]
  onChange: (filters: Record<string, any>) => void
  disabled?: boolean
}

export default function ModularFilter({ flags, onChange, disabled = false }: FilterProps) {
  const [filters, setFilters] = useState<Record<string, any>>({})

  const updateFilter = (key: string, value: any) => {
    const updated = { ...filters, [key]: value }
    setFilters(updated)
    onChange(updated)
  }

  return (
    <div
      className={`flex flex-wrap justify-evenly w-full gap-4 p-4 border rounded-md 
        ${disabled ? "bg-gray-200 dark:bg-gray-700 opacity-70 cursor-not-allowed" : "bg-gray-50 dark:bg-gray-800"}`}
    >
      {flags.map((flag) => {
        switch (flag.type) {
          case "select":
            return (
              <div
                key={flag.key}
                className={`flex min-w-48 max-w-xl justify-center items-center space-x-2 
                  ${disabled ? "text-gray-400 dark:text-gray-500" : "text-gray-700 dark:text-gray-300"}`}
              >
                <label className="text-sm font-medium">{flag.label}</label>
                <select
                  value={filters[flag.key] || ""}
                  onChange={(e) => updateFilter(flag.key, e.target.value)}
                  className={`border rounded px-2 py-1 
                    ${disabled ? "bg-gray-100 dark:bg-gray-600 cursor-not-allowed" : "dark:bg-gray-700 dark:text-gray-200"}`}
                  disabled={disabled}
                >
                  <option value="">Any</option>
                  {flag.options?.map((opt) => (
                    <option key={opt} value={opt}>
                      {opt}
                    </option>
                  ))}
                </select>
              </div>
            )

          default: // checkbox/toggle fallback
            return (
              <label
                key={flag.key}
                className={`flex min-w-48 max-w-xl justify-center items-center space-x-2 
                  ${disabled ? "text-gray-400 dark:text-gray-500 cursor-not-allowed" : "text-gray-700 dark:text-gray-300"}`}
              >
                <input
                  type="checkbox"
                  checked={!!filters[flag.key]}
                  onChange={(e) => updateFilter(flag.key, e.target.checked)}
                  className="rounded"
                  disabled={disabled}
                />
                <span>{flag.label}</span>
              </label>
            )
        }
      })}
    </div>
  )
}
