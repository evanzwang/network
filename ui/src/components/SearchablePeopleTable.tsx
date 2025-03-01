"use client";

import React, { useState, useEffect } from 'react';
import PeopleTable from './PeopleTable';
import SearchPopup from './SearchPopup';

// Define the Person type
type Person = {
  name: string;
  imageUrl: string;
  description: string;
  contacts: string[];
  matchReason?: string;
};

interface SearchablePeopleTableProps {
  people: Person[];
}

const SearchablePeopleTable: React.FC<SearchablePeopleTableProps> = ({ people }) => {
  const [isSearchPopupOpen, setIsSearchPopupOpen] = useState(false);
  const [filteredPeople, setFilteredPeople] = useState<Person[]>(people);
  const [searchQuery, setSearchQuery] = useState<string | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [isLoadingReasons, setIsLoadingReasons] = useState(false);

  // Update filtered people when people prop changes
  useEffect(() => {
    setFilteredPeople(people);
  }, [people]);

  // Fetch match reasons for the filtered people
  const fetchMatchReasons = async (query: string, matchedPeople: Person[]) => {
    if (!query || matchedPeople.length === 0) return;
    
    setIsLoadingReasons(true);
    try {
      // Get the names of the matched people
      const names = matchedPeople.map(person => person.name).join(',');
      
      console.log('Fetching reasons for query:', query);
      console.log('Names:', names);
      
      // Call the API to get the match reasons
      const response = await fetch(`http://127.0.0.1:8000/api/reasons/?text=${encodeURIComponent(query)}&names=${encodeURIComponent(names)}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Received reasons data:', data);
      
      // Update the filtered people with their match reasons
      if (data.reasons && typeof data.reasons === 'object') {
        const updatedPeople = matchedPeople.map(person => ({
          ...person,
          matchReason: data.reasons[person.name] || null
        }));
        
        console.log('Updated people with reasons:', updatedPeople);
        setFilteredPeople(updatedPeople);
      } else {
        console.warn('No valid reasons data received:', data);
      }
    } catch (error) {
      console.error('Error fetching match reasons:', error);
      // We don't set an error state here as it's not critical - we'll just show the results without reasons
    } finally {
      setIsLoadingReasons(false);
    }
  };

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    setIsSearching(true);
    setSearchError(null);
    
    // Close the popup immediately when search is clicked
    setIsSearchPopupOpen(false);
    
    try {
      // Call the backend API for search
      const response = await fetch(`http://127.0.0.1:8000/api/match/?text=${encodeURIComponent(query)}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const data = await response.json();
      const matchedPeople = data.matches || [];
      setFilteredPeople(matchedPeople);
      
      // After getting the matches, fetch the reasons
      if (matchedPeople.length > 0) {
        await fetchMatchReasons(query, matchedPeople);
      }
    } catch (error) {
      console.error('Error searching people:', error);
      setSearchError('Failed to search using the API. Falling back to local search.');
      // Fallback to client-side search if API call fails
      performClientSideSearch(query);
    } finally {
      setIsSearching(false);
    }
  };

  // Fallback client-side search function
  const performClientSideSearch = (query: string) => {
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
      const personText = `${person.name.toLowerCase()} ${person.description.toLowerCase()} ${person.contacts.join(' ').toLowerCase()}`;
      
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
    setSearchError(null);
  };

  // Determine if we should show match reasons
  const shouldShowMatchReasons = searchQuery !== null && filteredPeople.some(person => person.matchReason);
  
  console.log('Should show match reasons:', shouldShowMatchReasons);
  console.log('Filtered people with reasons:', filteredPeople.filter(p => p.matchReason));

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
          {searchError && (
            <div className="text-sm text-amber-600 dark:text-amber-400 mt-1">
              {searchError}
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
      
      {!isSearching && filteredPeople.length === 0 && searchQuery && (
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
      
      <div className="relative">
        {(isSearching || isLoadingReasons) && (
          <div className="absolute top-0 left-0 right-0 flex justify-center pt-4 z-10">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-lg flex items-center gap-3">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-solid border-blue-600 border-r-transparent"></div>
              <p className="text-gray-600 dark:text-gray-300">
                {isSearching ? 'Searching for matches...' : 'Loading match reasons...'}
              </p>
            </div>
          </div>
        )}
        
        <div className={`transition-all duration-300 ${isSearching || isLoadingReasons ? 'filter blur-sm opacity-50' : ''}`}>
          {((isSearching || isLoadingReasons) || filteredPeople.length > 0) && (
            <PeopleTable 
              people={filteredPeople} 
              showMatchReasons={shouldShowMatchReasons}
            />
          )}
        </div>
      </div>
      
      <SearchPopup 
        isOpen={isSearchPopupOpen}
        onClose={() => setIsSearchPopupOpen(false)}
        onSearch={handleSearch}
        isSearching={isSearching}
      />
    </div>
  );
};

export default SearchablePeopleTable; 