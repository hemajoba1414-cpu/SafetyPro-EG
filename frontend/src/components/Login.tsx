'use client';

import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';

export default function LoginComponent() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth(); // دالة اللوجين من السياق
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // 1. محاولة تسجيل الدخول
      await login(email, password);
      
      // 2. إذا نجح الكود سيصل هنا، فنقوم بالتحويل للداشبورد فوراً
      console.log("Login Successful! Redirecting...");
      
      // ملاحظة: استخدمت window.location كبديل أقوى في حالة وجود تعليق في الـ Router
      window.location.href = '/dashboard'; 
      
    } catch (err: any) {
      // 3. عرض رسالة الخطأ الحقيقية اللي جاية من السيرفر
      console.error("Detailed Login Error:", err);
      setError('خطأ في الدخول.. تأكد من الإيميل وكلمة المرور يا هندسة');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-gray-50">
      <div className="w-full max-w-md p-8 bg-white rounded-xl shadow-lg">
        <h1 className="text-3xl font-bold text-center mb-8 text-blue-600">Safety First</h1>
        <h2 className="text-xl font-semibold mb-6 text-right">تسجيل الدخول</h2>

        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg text-right animate-pulse">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2 text-right">
              البريد الإلكتروني
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-left"
              placeholder="your@email.com"
              dir="ltr"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2 text-right">
              كلمة المرور
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-left"
              placeholder="••••••••"
              dir="ltr"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded-lg transition disabled:bg-gray-400 flex justify-center items-center"
          >
            {loading ? (
              <>
                <span className="ml-2">جاري التحقق...</span>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              </>
            ) : 'دخول'}
          </button>
        </form>

        <p className="mt-4 text-center text-gray-600">
          ليس لديك حساب؟{' '}
          <a href="/auth/register" className="text-blue-600 hover:underline">
            اشترك الآن
          </a>
        </p>
      </div>
    </div>
  );
}