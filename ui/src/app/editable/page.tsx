'use client';

import React from 'react';
import EditablePeopleTable from '../../components/EditablePeopleTable';
import Link from 'next/link';

export default function EditablePage() {
  return (
    <div className="min-h-screen p-8 pb-20 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <div className="max-w-6xl mx-auto">
        <header className="mb-12">
          <h1 className="text-3xl font-bold mb-4">Editable People Directory</h1>
          <p className="text-gray-600 dark:text-gray-300 mb-4">
            Add, edit, or remove people from the directory
          </p>
          <Link 
            href="/"
            className="text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-300"
          >
            ← Back to main page
          </Link>
        </header>
        
        <main>
          <EditablePeopleTable />
        </main>
        
        <footer className="mt-16 text-center text-sm text-gray-500 dark:text-gray-400">
          <p>People Directory - Edit Mode</p>
        </footer>
      </div>
    </div>
  );
} 