type ErrorProps = {
  error: string;
};

export const Error = ({ error }: ErrorProps) => {
  return (
    <div className="w-full h-full mx-auto my-8 px-4">
      <div className="flex items-center gap-3 rounded-lg border border-red-300 dark:border-red-600 bg-red-50 dark:bg-red-900/30 text-red-800 dark:text-red-200 font-medium p-4 shadow-sm">
        <span>
          <strong>System Failure:</strong> {error}
        </span>
      </div>
    </div>
  );
};
