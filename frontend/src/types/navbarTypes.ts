export type dropDownItem = {
  name: string;
  href: string;
  element: React.ReactNode;
};
export type navigationType = {
  name: string;
  href: string;
  element?: React.ReactNode;
  current: boolean;
  dropdown?: boolean;
  dropdownItems?: dropDownItem[];
  requiresAccount: boolean;
};
