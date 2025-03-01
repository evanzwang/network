"use client";

import Image from 'next/image';
import React from 'react';

// Define the Person type
type Person = {
  id: number;
  name: string;
  imageUrl: string;
  description: string;
};


interface PeopleTableProps {
  people: Person[];
}

const PeopleTable: React.FC<PeopleTableProps> = ({ people }) => {
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
          {people.map((person) => (
            <tr key={person.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                {person.name}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="relative h-12 w-12 rounded-full overflow-hidden">
                  <Image
                    src={person.imageUrl}
                    alt={`${person.name}'s profile picture`}
                    fill
                    className="object-cover"
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