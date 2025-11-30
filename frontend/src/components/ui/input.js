import React from "react";

export const Input = ({ className = "", ...props }) => {
  return (
    <input
      className={`border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${className}`}
      {...props}
    />
  );
};
