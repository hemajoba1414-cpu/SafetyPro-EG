'use client';

import { ProtectedRoute } from '@/components/ProtectedRoute';

export default function SuccessPage() {
  return (
    <ProtectedRoute>
      <div className="flex h-screen items-center justify-center bg-green-50">
        <div className="text-center">
          <div className="text-6xl mb-4">✅</div>
          <h1 className="text-3xl font-bold text-green-600 mb-2">تم الدفع بنجاح!</h1>
          <p className="text-gray-600 mb-6">شكراً لك على اشتراكك</p>
          <a
            href="/dashboard"
            className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg"
          >
            العودة إلى لوحة التحكم
          </a>
        </div>
      </div>
    </ProtectedRoute>
  );
}
