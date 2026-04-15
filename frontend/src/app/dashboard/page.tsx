'use client';
import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { generatePlan } from '@/lib/api';
import Link from 'next/link';

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const [project, setProject] = useState('');
  const [loading, setLoading] = useState(false);
  const [planResult, setPlanResult] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!project.trim()) return;
    setLoading(true);
    try {
      const data = await generatePlan(project, ["general"]);
      setPlanResult(data.plan_content);
    } catch (err) {
      alert("Error connecting to server");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 text-right" dir="rtl">
      <header className="bg-white shadow p-6 flex justify-between items-center">
        <button onClick={logout} className="text-red-600 font-bold">تسجيل خروج</button>
        <div>
          <h1 className="text-2xl font-bold text-blue-600">Safety First</h1>
          <p className="text-gray-600">مرحباً {user?.full_name}</p>
        </div>
      </header>

      <main className="max-w-6xl mx-auto p-8">
        <div className="bg-red-50 p-4 rounded-lg mb-6 border-r-4 border-red-500">
          <p className="text-lg">متبقي لك <b>{user?.remainingDays ?? 30} يوم</b> في الفترة التجريبية.</p>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-bold mb-4 text-blue-900">إصدار خطة سلامة تلقائياً</h2>
          <input
            type="text"
            placeholder="اسم المشروع..."
            className="w-full p-3 border rounded-xl mb-4"
            value={project}
            onChange={(e) => setProject(e.target.value)}
          />
          <button
            onClick={handleGenerate}
            disabled={loading}
            className="w-full bg-red-600 text-white p-4 rounded-xl font-bold disabled:bg-gray-400"
          >
            {loading ? 'جاري الإصدار...' : 'إصدار خطة السلامة فوراً'}
          </button>
        </div>

        {planResult && (
          <div className="bg-white p-8 rounded-2xl shadow-xl border-2 border-blue-100 mb-8 whitespace-pre-wrap">
            {planResult}
          </div>
        )}

        <div className="grid grid-cols-3 gap-6">
          <Link href="/dashboard/plans" className="bg-white p-6 rounded-lg shadow text-center">📋 خططي</Link>
          <Link href="/subscription" className="bg-white p-6 rounded-lg shadow text-center">💳 الاشتراك</Link>
          <Link href="/dashboard/plans/new" className="bg-white p-6 rounded-lg shadow text-center">➕ جديد</Link>
        </div>
      </main>
    </div>
  );
}