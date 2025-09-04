const Alerts: React.FC<{ pLoading: boolean; pError: string | null; variantError: string | null }> = ({
    pLoading,
    pError,
    variantError,
}) => (
    <div className="mt-3 space-y-2">
        {pLoading && (
            <div className="rounded-lg border border-blue-200 bg-blue-50 text-blue-900 p-3 text-sm" aria-live="polite">
                Loading parameters…
            </div>
        )}
        {!!pError && (
            <div className="rounded-lg border border-amber-200 bg-amber-50 text-amber-900 p-3 text-sm" aria-live="polite">
                Parameters failed to load; showing last known values.
            </div>
        )}
        {!!variantError && (
            <div className="rounded-lg border border-red-200 bg-red-50 text-red-900 p-3 text-sm" aria-live="polite">
                {variantError}
            </div>
        )}
    </div>
);

export default Alerts