

type InputComponentProps = {
  id: string;
  type: React.HTMLInputTypeAttribute;
  name: string;
  label: string;
  placeholder?: string;
  required?: boolean;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
};
export default function FormInputTextBase({
  id,
  type,
  name,
  label,
  placeholder,
  required,
  onChange,
}: InputComponentProps) {
  return (
    <>
      <div className="mt-2 w-1/2 min-w-[200px]">
        <label className="block text-sm font-medium text-black" htmlFor={label}>
          {label}
        </label>
        <input
          type={type}
          id={id}
          name={name}
          placeholder={placeholder}
          required={required}
          onChange={onChange}
          className="block w-full  rounded-md bg-white/5 px-3 py-1.5 text-base text-black outline-1 outline-black placeholder:text-gray-500 focus:outline-2 focus:outline-indigo-500 sm:text-sm"
        />
      </div>
    </>
  );
}