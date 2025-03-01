"use client";

import Image from 'next/image';
import React, { useState } from 'react';

// Define the Person type
type Person = {
  name: string;
  imageUrl: string;
  description: string;
  contacts: string[];
};


interface PeopleTableProps {
  people: Person[];
}

const PeopleTable: React.FC<PeopleTableProps> = ({ people }) => {
  // State to track image loading errors
  const [imageErrors, setImageErrors] = useState<Record<number, boolean>>({});

  // Default fallback image URL
  const fallbackImageUrl = "https://randomuser.me/api/portraits/lego/1.jpg";

  // Handle image error
  const handleImageError = (index: number) => {
    setImageErrors(prev => ({
      ...prev,
      [index]: true
    }));
  };

  // Sort people by name
  const sortedPeople = [...people].sort((a, b) => a.name.localeCompare(b.name));

  return (
    <div className="w-full overflow-x-auto">
      <table className="min-w-full bg-white dark:bg-gray-800 rounded-lg overflow-hidden">
        <thead className="bg-gray-100 dark:bg-gray-700">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              Name
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              Picture
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              Description
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 dark:divide-gray-600">
          {sortedPeople.map((person, index) => (
            <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                {person.name}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="relative h-12 w-12 rounded-full overflow-hidden">
                  <Image
                    src={imageErrors[index] ? fallbackImageUrl : person.imageUrl}
                    alt={`${person.name}'s profile picture`}
                    fill
                    className="object-cover"
                    onError={() => handleImageError(index)}
                    unoptimized={true}
                  />
                </div>
              </td>
              <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-300">
                {person.description}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default PeopleTable; 