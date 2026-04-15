export default function Home() {
  return (
    <div className="flex h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-4">
          Safety First System 🔥
        </h1>

        <p className="mb-6">
          نظام إدارة السلامة المهنية
        </p>

        <a
          href="/auth/login"
          className="bg-blue-600 text-white px-6 py-3 rounded-lg"
        >
          تسجيل الدخول
        </a>
      </div>
    </div>
  );
}