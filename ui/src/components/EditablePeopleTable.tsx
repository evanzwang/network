import Image from 'next/image';
import React, { useState } from 'react';

// Define the Person type
export type Person = {
  id: number;
  name: string;
  imageUrl: string;
  description: string;
};

// Sample data for demonstration
const samplePeople: Person[] = [
  {
    id: 1,
    name: 'Jane Doe',
    imageUrl: 'https://randomuser.me/api/portraits/women/1.jpg',
    description: 'Software Engineer with 5 years of experience in web development.'
  },
  {
    id: 2,
    name: 'John Smith',
    imageUrl: 'https://randomuser.me/api/portraits/men/1.jpg',
    description: 'Product Manager specializing in SaaS products and user experience.'
  },
  {
    id: 3,
    name: 'Emily Johnson',
    imageUrl: 'https://randomuser.me/api/portraits/women/2.jpg',
    description: 'UX Designer with a passion for creating intuitive user interfaces.'
  },
];

interface EditablePeopleTableProps {
  initialPeople?: Person[];
}

const EditablePeopleTable: React.FC<EditablePeopleTableProps> = ({ initialPeople = samplePeople }) => {
  const [people, setPeople] = useState<Person[]>(initialPeople);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [newPerson, setNewPerson] = useState<Omit<Person, 'id'>>({
    name: '',
    imageUrl: '',
    description: ''
  });

  // Form for adding a new person
  const handleAddPerson = (e: React.FormEvent) => {
    e.preventDefault();
    const newId = people.length > 0 ? Math.max(...people.map(p => p.id)) + 1 : 1;
    setPeople([...people, { id: newId, ...newPerson }]);
    setNewPerson({ name: '', imageUrl: '', description: '' });
  };

  // Handle editing a person
  const handleEditPerson = (id: number) => {
    const personToEdit = people.find(p => p.id === id);
    if (personToEdit) {
      setEditingId(id);
    }
  };

  // Save edited person
  const handleSaveEdit = (id: number, updatedPerson: Partial<Person>) => {
    setPeople(people.map(p => p.id === id ? { ...p, ...updatedPerson } : p));
    setEditingId(null);
  };

  // Delete a person
  const handleDeletePerson = (id: number) => {
    setPeople(people.filter(p => p.id !== id));
  };

  return (
    <div className="w-full space-y-8">
      <div className="overflow-x-auto">
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
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-600">
            {people.map((person) => (
              <tr key={person.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                  {editingId === person.id ? (
                    <input
                      type="text"
                      className="border rounded px-2 py-1 w-full dark:bg-gray-700 dark:text-white"
                      value={person.name}
                      onChange={(e) => handleSaveEdit(person.id, { name: e.target.value })}
                    />
                  ) : (
                    person.name
                  )}
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
                  {editingId === person.id && (
                    <input
                      type="text"
                      className="border rounded px-2 py-1 mt-2 w-full dark:bg-gray-700 dark:text-white text-xs"
                      value={person.imageUrl}
                      onChange={(e) => handleSaveEdit(person.id, { imageUrl: e.target.value })}
                      placeholder="Image URL"
                    />
                  )}
                </td>
                <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-300">
                  {editingId === person.id ? (
                    <textarea
                      className="border rounded px-2 py-1 w-full dark:bg-gray-700 dark:text-white"
                      value={person.description}
                      onChange={(e) => handleSaveEdit(person.id, { description: e.target.value })}
                    />
                  ) : (
                    person.description
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  {editingId === person.id ? (
                    <button
                      onClick={() => setEditingId(null)}
                      className="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300 mr-3"
                    >
                      Done
                    </button>
                  ) : (
                    <button
                      onClick={() => handleEditPerson(person.id)}
                      className="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300 mr-3"
                    >
                      Edit
                    </button>
                  )}
                  <button
                    onClick={() => handleDeletePerson(person.id)}
                    className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Form to add a new person */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">Add New Person</h3>
        <form onSubmit={handleAddPerson} className="space-y-4">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Name
            </label>
            <input
              type="text"
              id="name"
              required
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              value={newPerson.name}
              onChange={(e) => setNewPerson({ ...newPerson, name: e.target.value })}
            />
          </div>
          <div>
            <label htmlFor="imageUrl" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Image URL
            </label>
            <input
              type="text"
              id="imageUrl"
              required
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              value={newPerson.imageUrl}
              onChange={(e) => setNewPerson({ ...newPerson, imageUrl: e.target.value })}
              placeholder="https://example.com/image.jpg"
            />
          </div>
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Description
            </label>
            <textarea
              id="description"
              required
              rows={3}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              value={newPerson.description}
              onChange={(e) => setNewPerson({ ...newPerson, description: e.target.value })}
            />
          </div>
          <div>
            <button
              type="submit"
              className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Add Person
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditablePeopleTable; 