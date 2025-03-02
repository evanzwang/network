"use client";

import Image from "next/image";
import Link from "next/link";
import { useState, useEffect } from "react";
import SearchablePeopleTable from "../components/SearchablePeopleTable";

// Define the Person type
type Person = {
  name: string;
  imageUrl: string;
  description: string;
  contacts: string[];
};

export default function Home() {
  const [people, setPeople] = useState<Person[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch people data from the API
  useEffect(() => {
    const fetchPeople = async () => {
      try {
        setIsLoading(true);
        const response = await fetch('https://3.145.209.248/api/people/');
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log(data);
        setPeople(data.people);
        setIsLoading(false);
      } catch (err) {
        console.error('Error fetching people:', err);
        setError('Failed to load people data. Please try again later.');
        setIsLoading(false);
      }
    };

    fetchPeople();
  }, []);

  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <main className="flex flex-col gap-8 row-start-2 items-center w-full max-w-6xl">
        <h1 className="text-3xl font-bold mb-4 text-center">People Directory</h1>
        <p className="text-gray-600 dark:text-gray-300 mb-8 text-center">
          These are the people in our database. Ask a question!
        </p>
        
        {isLoading && (
          <div className="text-center py-8">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
            <p className="mt-2 text-gray-600 dark:text-gray-300">Loading people data...</p>
          </div>
        )}
        
        {error && (
          <div className="text-center py-8 text-red-500">
            <p>{error}</p>
          </div>
        )}
        
        {!isLoading && !error && (
          <SearchablePeopleTable people={people} />
        )}
        
      </main>
      <footer className="row-start-3 flex gap-6 flex-wrap items-center justify-center">
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://nextjs.org/learn?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/file.svg"
            alt="File icon"
            width={16}
            height={16}
          />
          Learn
        </a>
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://vercel.com/templates?framework=next.js&utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/window.svg"
            alt="Window icon"
            width={16}
            height={16}
          />
          Examples
        </a>
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://nextjs.org?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/globe.svg"
            alt="Globe icon"
            width={16}
            height={16}
          />
          Go to nextjs.org →
        </a>
      </footer>
    </div>
  );
}
