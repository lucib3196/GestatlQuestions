import {
  Disclosure,
  DisclosureButton,
  DisclosurePanel,
  Menu,
  MenuButton,
  MenuItem,
  MenuItems,
} from "@headlessui/react";

import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
} from 'react-router-dom';
import { Bars3Icon, XMarkIcon } from "@heroicons/react/24/outline";
import { ChevronDownIcon } from '@heroicons/react/20/solid'
import TextGenerator from "./CodeGenerators/TextGenerator";

import MainQuestionView from "../pages/MainQuestionView";
import type React from "react";
import ImageGenerator from "./CodeGenerators/ImageGenerator";

type dropDownItem = {
  name: string,
  href: string,
  element: React.ReactNode,
}
type navigationType = {
  name: string;
  href: string;
  element?: React.ReactNode
  current: boolean;
  dropdown?: boolean
  dropdownItems?: dropDownItem[]
}
const navigation: navigationType[] = [
  { name: "Questions", href: "/questions", element: <MainQuestionView />, current: false },
  {
    name: "Generators", href: "/generators", current: false, dropdown: true, dropdownItems: [
      { name: "Text", href: "/generators/text_generator", element: <TextGenerator /> },
      { name: "ImageUpload", href: "/generators/image_generator", element: <ImageGenerator /> },
    ]
  },
];

function NavBar() {
  return (
    <Router>
      <Disclosure as="nav" className="bg-gray-800">
        <div className="mx-auto max-w-7xl px-2 sm:px-6 lg:px-8">
          <div className="relative flex h-16 items-center justify-between">
            {/* Mobile Menu Button */}
            <div className="absolute inset-y-0 left-0 flex items-center sm:hidden">
              <DisclosureButton className="group relative inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-gray-700 hover:text-white focus:outline-none focus:ring-2 focus:ring-white">
                <span className="sr-only">Open main menu</span>
                <Bars3Icon className="block h-6 w-6 group-data-open:hidden" aria-hidden="true" />
                <XMarkIcon className="hidden h-6 w-6 group-data-open:block" aria-hidden="true" />
              </DisclosureButton>
            </div>

            {/* Desktop Menu */}
            <div className="flex flex-1 items-center justify-center sm:items-stretch sm:justify-start">
              <div className="hidden sm:ml-6 sm:block">
                <div className="flex space-x-4 items-center">
                  {navigation.map((item) =>
                    item.dropdown ? (
                      <Menu key={item.name}>
                        <MenuButton className="flex items-center text-white space-x-1">
                          <span>{item.name}</span>
                          <ChevronDownIcon className="h-4 w-4 fill-white/60" />
                        </MenuButton>
                        <MenuItems transition
                          anchor="bottom" className=" flex flex-col justify-center items-center mt-2 w-40 rounded-xl border border-white/20 bg-gray-800 p-1 text-white text-sm shadow-lg ring-1 ring-black/5 focus:outline-none">
                          {item.dropdownItems?.map((ditem) => (
                            <MenuItem key={ditem.name}>
                              <Link
                                to={ditem.href}
                                className="block px-3 py-2 rounded-md hover:bg-white/10"
                              >
                                {ditem.name}
                              </Link>
                            </MenuItem>
                          ))}
                        </MenuItems>
                      </Menu>
                    ) : (
                      <Link
                        key={item.name}
                        to={item.href}
                        className={`px-3 py-2 rounded-md text-base font-medium text-gray-300 hover:bg-gray-700 hover:text-white'
                        }`}
                      >
                        {item.name}
                      </Link>
                    )
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        <DisclosurePanel className="sm:hidden">
          <div className="space-y-1 px-2 pt-2 pb-3">
            {navigation.map((item) => (
              <DisclosureButton key={item.name} as={Link} to={item.href} >
                <span
                  className={'block rounded-md px-3 py-2 text-base font-medium text-gray-300 hover:bg-gray-700 hover:text-white'
                  }
                >
                  {item.name}
                </span>
              </DisclosureButton>
            ))}
          </div>
        </DisclosurePanel>
      </Disclosure>

      <Routes>
        <Route path="/questions" element={<MainQuestionView />} />
        <Route path="/generators/text_generator" element={<TextGenerator />} />
        <Route path="/generators/image_generator" element={<ImageGenerator />} />
        {/* <Route path="*" element={<NotFound />} */}
      </Routes>
    </Router>
  );
}

export default NavBar