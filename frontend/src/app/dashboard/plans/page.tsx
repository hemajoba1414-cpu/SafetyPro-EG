'use client';

import { ProtectedRoute } from '@/components/ProtectedRoute';
import PlansComponent from '@/components/Plans';

export default function PlansPage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow">
          <div className="max-w-6xl mx-auto px-4 py-6 flex justify-between items-center">
            <a href="/dashboard" className="text-blue-600 hover:underline">
              ← العودة
            </a>
            <h1 className="text-3xl font-bold text-blue-600">Safety First</h1>
          </div>
        </header>
        <main className="max-w-6xl mx-auto px-4 py-8">
          <PlansComponent />
        </main>
      </div>
    </ProtectedRoute>
  );
}
