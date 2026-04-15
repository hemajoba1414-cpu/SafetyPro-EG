'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Subscription, PricingPlan } from '@/types';

export default function SubscriptionComponent() {
  const [currentSubscription, setCurrentSubscription] = useState<Subscription | null>(null);
  const [plans, setPlans] = useState<PricingPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [checkoutLoading, setCheckoutLoading] = useState<string | null>(null);
  const { token } = useAuth();

  useEffect(() => {
    fetchSubscription();
    fetchPlans();
  }, [token]);

  const fetchSubscription = async () => {
    try {
      const response = await fetch('http://localhost:8000/subscriptions/current', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setCurrentSubscription(data);
      }
    } catch (error) {
      console.error('Error fetching subscription:', error);
    }
  };

  const fetchPlans = async () => {
    try {
      const response = await fetch('http://localhost:8000/subscriptions/pricing');
      if (response.ok) {
        const data = await response.json();
        setPlans(data.plans);
      }
    } catch (error) {
      console.error('Error fetching plans:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (planType: string) => {
    if (planType === 'free') return;

    setCheckoutLoading(planType);
    try {
      const response = await fetch('http://localhost:8000/subscriptions/checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ plan_type: planType }),
      });

      if (response.ok) {
        const data = await response.json();
        window.location.href = data.checkout_url;
      }
    } catch (error) {
      console.error('Error creating checkout session:', error);
    } finally {
      setCheckoutLoading(null);
    }
  };

  if (loading) {
    return <div className="text-center py-8">جاري التحميل...</div>;
  }

  const currentPlanIndex = [
    'free',
    'starter',
    'professional',
    'enterprise',
  ].indexOf(currentSubscription?.plan_type || 'free');

  return (
    <div className="py-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-right mb-2">خطط الاشتراك</h1>
        <p className="text-gray-600 text-right mb-8">
          اختر الخطة المناسبة لاحتياجاتك. الخطة الحالية:{' '}
          <span className="font-semibold text-blue-600">
            {currentSubscription?.plan_type.toUpperCase()}
          </span>
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {plans.map((plan, index) => (
            <div
              key={plan.name}
              className={`rounded-lg border-2 p-6 transition ${
                index === currentPlanIndex
                  ? 'border-blue-600 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <h3 className="text-xl font-bold mb-2 text-right">{plan.name}</h3>
              <div className="text-3xl font-bold mb-4 text-right">
                ${plan.price}
                <span className="text-sm text-gray-600">/شهر</span>
              </div>
              <p className="text-sm text-gray-600 mb-4 text-right">
                حد أقصى {plan.max_plans} خطة
              </p>

              <ul className="space-y-2 mb-6 text-right">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center justify-end gap-2">
                    <span className="text-green-600">✓</span>
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>

              {index === currentPlanIndex ? (
                <button
                  disabled
                  className="w-full py-2 bg-gray-400 text-white rounded-lg font-semibold"
                >
                  الخطة الحالية
                </button>
              ) : (
                <button
                  onClick={() => handleUpgrade(plan.name.toLowerCase())}
                  disabled={checkoutLoading !== null}
                  className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition disabled:bg-gray-400"
                >
                  {checkoutLoading === plan.name.toLowerCase()
                    ? 'جاري التحويل...'
                    : 'اختر'}
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
