import { useState, useEffect } from "react";
import { signUp, login, loginWithGoogle, setupRecaptcha } from "../AuthServices";

export default function LoginSignup() {

  const [isLogin, setIsLogin] = useState(false);
  const [showPhoneLogin, setShowPhoneLogin] = useState(false);

  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("");
  const [confirmationResult, setConfirmationResult] = useState(null);

  const [otpTimer, setOtpTimer] = useState(0);

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let interval;

    if (otpTimer > 0) {
      interval = setInterval(() => {
        setOtpTimer((prev) => prev - 1);
      }, 1000);
    }

    return () => clearInterval(interval);
  }, [otpTimer]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!fullName) {
      alert("Username is required");
      return;
    }

    if (!isLogin && password !== confirmPassword) {
      alert("Passwords do not match");
      return;
    }

    setLoading(true);

    try {
      if (isLogin) {
        await login(email, password);
        alert("Logged in successfully");
      } else {
        await signUp(email, password, fullName);
        alert("Account created successfully");
      }
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const sendOTP = async () => {

    if (!fullName) {
      alert("Username is required");
      return;
    }

    try {
      const result = await setupRecaptcha(phone);
      setConfirmationResult(result);
      setOtpTimer(30);
      alert("OTP sent!");
    } catch (err) {
      alert(err.message);
    }
  };

  const verifyOTP = async () => {
    try {
      await confirmationResult.confirm(otp);
      alert("Phone login successful");
    } catch (err) {
      alert("Invalid OTP");
    }
  };

  const handleGoogleLogin = async () => {
    try {
      await loginWithGoogle();
      alert("Logged in with Google");
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0f172a] text-white p-4">

      <div className="relative backdrop-blur-xl bg-white/10 p-8 rounded-2xl shadow-2xl  border-white/20 w-full max-w-md">

        <h1 className="text-xl font-extrabold mb-8 text-center bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
          {showPhoneLogin ? "Login by phone" : isLogin ? "Log In" : "Sign Up"}
        </h1>

        {!showPhoneLogin && (
          <>
            <form className="space-y-5" onSubmit={handleSubmit}>

              <input
                type="text"
                placeholder="Username"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full p-3 rounded-xl bg-white/5 border border-white/10"
              />

              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full p-3 rounded-xl bg-white/5 border border-white/10"
              />

              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full p-3 rounded-xl bg-white/5 border border-white/10"
              />

              {!isLogin && (
                <input
                  type="password"
                  placeholder="Re-enter Password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full p-3 rounded-xl bg-white/5 border border-white/10"
                />
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 rounded-xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 transition-all"
              >
                {loading ? "Processing..." : isLogin ? "Log In" : "Sign Up"}
              </button>

            </form>

            <button
              type="button"
              onClick={handleGoogleLogin}
              className="w-full mt-4 flex items-center justify-center gap-3 bg-white text-gray-800 font-semibold py-3 rounded-xl border border-gray-300 shadow-md hover:bg-gray-500 hover:shadow-lg transition-all duration-200"
              style={{ backgroundColor: "#ffffff", color: "#1f2937" }}
            >
              <img
                src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
                alt="Google"
                className="w-5 h-5"
              />
              Continue with Google
            </button>

            <p className="text-center mt-4 text-sm">
              <button
                onClick={() => setShowPhoneLogin(true)}
                className="border-none px-4 py-2 rounded-lg font-semibold outline-none hover:text-blue-500 hover:underline focus:outline-none"
                style={{ border: "none", outline: "none", boxShadow: "none", appearance: "none", WebkitAppearance: "none" }}
              >
                Another way to login
              </button>
            </p>
          </>
        )}

        {showPhoneLogin && (
          <div className="space-y-4">

            <input
              type="text"
              placeholder="Username"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full p-3 rounded-xl bg-white/5 border border-white/10"
            />

            <input
              type="tel"
              placeholder="+91XXXXXXXXXX"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="w-full p-3 rounded-xl bg-white/5 border border-white/10"
            />

            <button
              onClick={sendOTP}
              className="w-full py-3 rounded-xl font-semibold bg-gradient-to-r from-green-600 to-emerald-500 hover:from-green-500 hover:to-emerald-400"
            >
              Send OTP
            </button>

            {otpTimer > 0 && (
              <p className="text-sm text-blue-400 text-center">
                Enter OTP within {otpTimer}s
              </p>
            )}

            <input
              type="text"
              placeholder="Enter OTP"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              className="w-full p-3 rounded-xl bg-white/5 border border-white/10"
            />

            <button
              onClick={verifyOTP}
              className="w-full py-3 rounded-xl font-semibold bg-gradient-to-r from-blue-600 to-indigo-500 hover:from-blue-500 hover:to-indigo-400"
            >
              Verify OTP
            </button>

            {otpTimer === 0 && confirmationResult && (
              <button
                onClick={sendOTP}
                className="w-full py-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-500 hover:from-blue-500 hover:to-indigo-400"
              >
                Resend OTP
              </button>
            )}

            <div id="recaptcha-container"></div>

            <button
              onClick={() => setShowPhoneLogin(false)}
              className="w-full rounded-xl border-none bg-slate-800 py-2 outline-none hover:bg-slate-700 focus:outline-none"
              style={{ border: "none", outline: "none", boxShadow: "none", appearance: "none", WebkitAppearance: "none" }}
            >
              ← Back
            </button>

          </div>
        )}

        {!showPhoneLogin && (
          <p className="text-center border-0 mt-6 text-sm">
            {isLogin ? "New user?" : "Already have an account?"}{" "}
            <button
              onClick={() => setIsLogin(!isLogin)}
              className="border-none font-bold text-cyan-400 outline-none hover:underline focus:outline-none"
              style={{ border: "none", outline: "none", boxShadow: "none", appearance: "none", WebkitAppearance: "none" }}
            >
              {isLogin ? "Sign Up" : "Log In"}
            </button>
          </p>
        )}

      </div>
    </div>
  );
}