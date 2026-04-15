"use client";
import { useState } from "react";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async () => {
    const res = await fetch("http://localhost:8000/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    localStorage.setItem("token", data.access_token);
    window.location.href = "/dashboard";
  };

  return (
    <div className="flex h-screen items-center justify-center">
      <div className="p-6 bg-white rounded-xl shadow">
        <h2 className="text-xl mb-4">تسجيل الدخول</h2>
        <input placeholder="Email" onChange={(e)=>setEmail(e.target.value)} className="border p-2 mb-2 w-full" />
        <input type="password" placeholder="Password" onChange={(e)=>setPassword(e.target.value)} className="border p-2 mb-2 w-full" />
        <button onClick={handleLogin} className="bg-blue-600 text-white px-4 py-2 w-full">دخول</button>
      </div>
    </div>
  );
}
