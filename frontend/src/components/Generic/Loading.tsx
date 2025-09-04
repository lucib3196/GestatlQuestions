export const Loading = () => {
    return (
        <div className="max-w-5xl mx-auto my-8 px-4">
            <div className="space-y-3">
                <div className="h-4 w-1/2 rounded bg-slate-200 animate-pulse" />
                Loading
                <div className="h-24 w-full rounded bg-slate-200 animate-pulse" />
            </div>
        </div>)
}