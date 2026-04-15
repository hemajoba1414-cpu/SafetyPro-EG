'use client';

export default function CancelledPage() {
  return (
    <div className="flex h-screen items-center justify-center bg-red-50">
      <div className="text-center">
        <div className="text-6xl mb-4">❌</div>
        <h1 className="text-3xl font-bold text-red-600 mb-2">تم إلغاء العملية</h1>
        <p className="text-gray-600 mb-6">لم يتم إتمام الدفع. يمكنك محاولة مرة أخرى</p>
        <a
          href="/subscription"
          className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg"
        >
          العودة إلى الاشتراك
        </a>
      </div>
    </div>
  );
}
