

export default function FileDropDown({
  fileNames,
  selectedFile,
  setSelectedFile,
}: {
  fileNames: string[];
  selectedFile: string;
  setSelectedFile: (val: string) => void;
}) {
  const handleFileChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedFile(event.target.value);
  };

  const cleaned = selectedFile.trim();

  return (
    <div className="w-full">
      <label
        htmlFor="fileDropDown"
        className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
      >
        Select File
      </label>

      <select
        id="fileDropDown"
        name="fileDropdown"
        value={cleaned}
        onChange={handleFileChange}
        className="w-full rounded-lg border border-gray-300 bg-white dark:bg-gray-800
                   text-gray-900 dark:text-gray-100 text-sm px-3 py-2
                   focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent
                   transition-colors duration-200 ease-in-out"
      >
        {fileNames.map((v) => (
          <option key={v} value={v.trim()}>
            {v.trim()}
          </option>
        ))}
      </select>
    </div>
  );
}