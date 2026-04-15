'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Plan } from '@/types';

export default function PlansComponent() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [loading, setLoading] = useState(true);
  const [downloadingId, setDownloadingId] = useState<number | null>(null);
  const { token } = useAuth();

  useEffect(() => {
    fetchPlans();
  }, [token]);

  const fetchPlans = async () => {
    try {
      const response = await fetch('http://localhost:8000/plans/', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setPlans(data);
      }
    } catch (error) {
      console.error('Error fetching plans:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async (planId: number) => {
    setDownloadingId(planId);
    try {
      const response = await fetch(`http://localhost:8000/export/pdf/${planId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        const binaryString = atob(data.pdf);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        const blob = new Blob([bytes], { type: 'application/pdf' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = data.filename;
        a.click();
      }
    } catch (error) {
      console.error('Error downloading PDF:', error);
    } finally {
      setDownloadingId(null);
    }
  };

  if (loading) {
    return <div className="text-center py-8">جاري التحميل...</div>;
  }

  return (
    <div className="py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-right mb-8">خططي الأمان</h1>

        {plans.length === 0 ? (
          <div className="text-center py-12 bg-gray-50 rounded-lg">
            <p className="text-gray-600 mb-4">لم تقم بإنشاء أي خطط أمان حتى الآن</p>
            <a
              href="/dashboard/plans/new"
              className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg"
            >
              إنشاء خطة جديدة
            </a>
          </div>
        ) : (
          <div className="space-y-4">
            {plans.map((plan) => (
              <div
                key={plan.id}
                className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition"
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1 text-right">
                    <h2 className="text-2xl font-bold text-gray-900">{plan.title}</h2>
                    <p className="text-gray-600 mt-1">{plan.description}</p>
                    <p className="text-sm text-gray-500 mt-2">
                      الحالة:{' '}
                      <span className="font-semibold text-blue-600">{plan.status}</span>
                    </p>
                  </div>
                  <button
                    onClick={() => handleDownloadPDF(plan.id)}
                    disabled={downloadingId === plan.id}
                    className="ml-4 bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-lg transition disabled:bg-gray-400"
                  >
                    {downloadingId === plan.id ? '⏳ تحميل...' : '📥 تحميل PDF'}
                  </button>
                </div>

                <div className="mt-4">
                  <h3 className="font-semibold text-right mb-2">خطوات الأمان:</h3>
                  <ol className="space-y-2 text-right">
                    {plan.steps.map((step, idx) => (
                      <li key={idx} className="text-sm text-gray-700">
                        <span className="font-semibold">{idx + 1}. {step.title}</span>
                        <p className="text-gray-600">{step.description}</p>
                      </li>
                    ))}
                  </ol>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
