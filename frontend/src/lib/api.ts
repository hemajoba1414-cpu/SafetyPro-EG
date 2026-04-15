const API_URL = https://safety-pro-eg-4793.vercel.app.";

// دالة موحدة لإضافة التوكن في كل الطلبات مع التأكد من وجوده
const getHeaders = () => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
};

export const generatePlan = async (projectName: string) => {
    const res = await fetch(`${API_URL}/generate-plan`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ projectName })
    });
    
    if (res.status === 401) {
        throw new Error("انتهت صلاحية الجلسة، برجاء تسجيل الدخول مرة أخرى");
    }
    
    if (!res.ok) throw new Error("حدث خطأ في السيرفر أثناء توليد الخطة");
    
    return res.json();
};

export const getUserPlans = async () => {
    const res = await fetch(`${API_URL}/my-plans`, {
        method: 'GET',
        headers: getHeaders()
    });
    
    if (!res.ok) return []; // إرجاع مصفوفة فارغة في حالة الخطأ لضمان عدم توقف الواجهة
    
    return res.json();
};