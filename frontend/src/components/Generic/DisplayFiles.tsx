type DisplayFileProps = {
    files: File[]
}

export function DisplayFiles({ files }: DisplayFileProps) {
    if (!files.length) {
        return (
            <p className="text-gray-500 dark:text-gray-400 text-sm text-center">
                No files selected
            </p>
        );
    }

    return (
        <div className="w-full max-w-md mx-auto mt-4 space-y-2">
            {files.map((f, idx) => (
                <div
                    key={idx}
                    className="flex items-center justify-between rounded-md border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 px-3 py-2 text-sm text-gray-800 dark:text-gray-200"
                >
                    <span className="truncate">{f.name}</span>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                        {(f.size / 1024).toFixed(1)} KB
                    </span>
                </div>
            ))}
        </div>
    );
}