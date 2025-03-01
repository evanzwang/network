"use client";

import React, { useState, useEffect } from 'react';
import PeopleTable from './PeopleTable';
import SearchPopup from './SearchPopup';

// Define the Person type
type Person = {
  id: number;
  name: string;
  imageUrl: string;
  description: string;
};

interface SearchablePeopleTableProps {
  people: Person[];
}

const SearchablePeopleTable: React.FC<SearchablePeopleTableProps> = ({ people }) => {
  const [isSearchPopupOpen, setIsSearchPopupOpen] = useState(false);
  const [filteredPeople, setFilteredPeople] = useState<Person[]>(people);
  const [searchQuery, setSearchQuery] = useState<string | null>(null);

  // Update filtered people when people prop changes
  useEffect(() => {
    setFilteredPeople(people);
  }, [people]);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    
    // Enhanced natural language search implementation
    const lowercaseQuery = query.toLowerCase();
    
    // Extract key terms from the query by removing common words
    const commonWords = ['a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'about', 'who', 'what', 'where', 'when', 'why', 'how', 'is', 'are', 'am', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'can', 'could', 'will', 'would', 'should', 'may', 'might', 'must', 'looking', 'find', 'search', 'people', 'person'];
    
    // Split the query into words and filter out common words
    const queryWords = lowercaseQuery
      .split(/\s+/)
      .filter(word => !commonWords.includes(word) && word.length > 1);
    
    // If no meaningful words remain, show all people
    if (queryWords.length === 0) {
      setFilteredPeople(people);
      return;
    }
    
    // Score each person based on how many query words match their data
    const scoredPeople = people.map(person => {
      const personText = `${person.name.toLowerCase()} ${person.description.toLowerCase()}`;
      
      // Calculate a score based on how many query words appear in the person's data
      let score = 0;
      for (const word of queryWords) {
        if (personText.includes(word)) {
          score += 1;
          
          // Give extra points for exact role matches (e.g., "developer", "engineer")
          if (person.description.toLowerCase().includes(word)) {
            score += 0.5;
          }
        }
      }
      
      return { person, score };
    });
    
    // Filter people with a score > 0 and sort by score (highest first)
    const filteredAndSorted = scoredPeople
      .filter(item => item.score > 0)
      .sort((a, b) => b.score - a.score)
      .map(item => item.person);
    
    setFilteredPeople(filteredAndSorted.length > 0 ? filteredAndSorted : []);
  };

  const clearSearch = () => {
    setFilteredPeople(people);
    setSearchQuery(null);
  };

  return (
    <div className="w-full flex flex-col gap-4">
      <div className="flex justify-between items-center">
        <div>
          {searchQuery && (
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500 dark:text-gray-400">
                Showing results for: <span className="font-medium">{searchQuery}</span>
              </span>
              <button 
                onClick={clearSearch}
                className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 text-sm"
              >
                Clear
              </button>
            </div>
          )}
        </div>
        <button
          onClick={() => setIsSearchPopupOpen(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Search People
        </button>
      </div>
      
      {filteredPeople.length === 0 && searchQuery && (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          <p>No people found matching your search criteria.</p>
          <button 
            onClick={clearSearch}
            className="mt-2 text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
          >
            Show all people
          </button>
        </div>
      )}
      
      {filteredPeople.length > 0 && (
        <PeopleTable people={filteredPeople} />
      )}
      
      <SearchPopup 
        isOpen={isSearchPopupOpen}
        onClose={() => setIsSearchPopupOpen(false)}
        onSearch={handleSearch}
      />
    </div>
  );
};

export default SearchablePeopleTable; 