import { useState } from "react";
import { signUp, login, loginWithGoogle } from "../authService"; // check path

export default function LoginSignup() {
   const [isLogin, setIsLogin] = useState(true);
  const [isClicked, setIsClicked] = useState(false);

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsClicked(true);
    setTimeout(() => setIsClicked(false), 500);

    setLoading(true); // start loading state 
    try {
      if (isLogin) {       
        await login(email, password);
        alert("✅ Logged in successfully");
      } else {
        await signUp(email, password);
        alert("✅ Account created successfully");
      }
    } catch (err) {
      alert("❌ " + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Google login handler
  const handleGoogleLogin = async () => {
    try {
      await loginWithGoogle();
      alert("✅ Logged in with Google");
    } catch (err) {
      alert("❌ " + err.message);
    }
  };


  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0f172a] text-white p-4">
      {/* Animated Background Blob */}
      <div className="absolute top-0 -left-4 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
      <div className="absolute bottom-0 -right-4 w-72 h-72 bg-cyan-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>

      <div className="relative backdrop-blur-xl bg-white/10 p-8 rounded-2xl shadow-2xl border border-white/20 w-full max-w-md transition-all duration-500">
        <h1 className="text-3xl font-extrabold mb-8 text-center bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
          {isLogin ? "Welcome Back" : "Create Account"}
        </h1>

        <form className="space-y-5" onSubmit={handleSubmit}>
          {!isLogin && (
            <input
              type="text"
              placeholder="Full Name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full p-3 rounded-xl bg-white/5 border border-white/10 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 outline-none transition-all placeholder:text-gray-500"
            />
          )}
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full p-3 rounded-xl bg-white/5 border border-white/10 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 outline-none transition-all placeholder:text-gray-500"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full p-3 rounded-xl bg-white/5 border border-white/10 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 outline-none transition-all placeholder:text-gray-500"
          />

          <button
            type="submit"
            disabled={loading}
            className={`w-full py-3 rounded-xl font-bold tracking-wide transition-all duration-300 transform 
              ${loading ? "bg-gray-600" : "bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 hover:shadow-[0_0_20px_rgba(168,85,247,0.4)] active:scale-95"}`}
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                Processing...
              </span>
            ) : isLogin ? "Sign In" : "Get Started"}
          </button>
        </form>

        <div className="relative my-8">
          <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-white/10"></div></div>
          <div className="relative flex justify-center text-xs uppercase"><span className="bg-[#1e293b] px-2 text-gray-400">Or continue with</span></div>
        </div>

        <button
          onClick={handleGoogleLogin}
          className="w-full flex items-center justify-center gap-3 bg-white hover:bg-gray-100 text-gray-900 font-semibold py-3 rounded-xl transition-all duration-300 transform hover:scale-[1.02]"
        >
          <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="Google" className="w-5 h-5" />
          Google
        </button>

        <p className="text-center mt-8 text-gray-400 text-sm">
          {isLogin ? "New here?" : "Joined us before?"}{" "}
          <button onClick={() => setIsLogin(!isLogin)} className="text-cyan-400 font-bold hover:underline underline-offset-4">
            {isLogin ? "Create an account" : "Log in to your dashboard"}
          </button>
        </p>
      </div>
    </div>
  );
}