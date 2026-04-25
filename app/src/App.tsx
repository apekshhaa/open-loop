import { useState, useEffect, useCallback, useRef } from 'react';
import {
  ChevronLeft,
  ChevronRight,
  ArrowRight,
  Heart,
  RefreshCw,
  Repeat,
  Bookmark,
  ExternalLink,
  X,
  Eye,
  EyeOff,
  Chrome,
  Apple,
  User,
  LockKeyhole,
  CheckCircle,
} from 'lucide-react';

/* ─── Types ─── */
interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error';
}

/* ─── Toast Component ─── */
function ToastNotification({ toast, onClose }: { toast: Toast; onClose: () => void }) {
  useEffect(() => {
    const timer = setTimeout(onClose, 3000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className="toast-enter fixed top-6 right-6 z-[60] flex items-center gap-3 rounded-xl border border-[rgba(245,240,232,0.1)] bg-[#1a1a24] px-5 py-4 shadow-2xl">
      <CheckCircle className="h-5 w-5 text-emerald-400" />
      <span className="text-sm font-medium text-[#F5F0E8]">{toast.message}</span>
      <button
        onClick={onClose}
        className="ml-2 text-[#8A8578] transition-colors hover:text-[#F5F0E8]"
        aria-label="Close toast"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
}

/* ─── Login/Signup Modal ─── */
function LoginSignupModal({
  isOpen,
  onClose,
  onSuccess,
}: {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (name?: string) => void;
}) {
  const [activeTab, setActiveTab] = useState<'signin' | 'signup'>('signin');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    agreeTerms: false,
  });
  const modalRef = useRef<HTMLDivElement>(null);
  const overlayRef = useRef<HTMLDivElement>(null);

  const handleClose = useCallback(() => {
    setIsClosing(true);
    setTimeout(() => {
      setIsClosing(false);
      onClose();
      setFormData({ fullName: '', email: '', password: '', confirmPassword: '', agreeTerms: false });
      setActiveTab('signin');
    }, 350);
  }, [onClose]);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) handleClose();
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, handleClose]);

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'hidden';
    }
  }, [isOpen]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (activeTab === 'signin') {
      onSuccess();
    } else {
      onSuccess(formData.fullName || 'New Member');
    }
    handleClose();
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === overlayRef.current) handleClose();
  };

  if (!isOpen) return null;

  return (
    <div
      ref={overlayRef}
      onClick={handleOverlayClick}
      className={`fixed inset-0 z-50 flex items-center justify-center ${isClosing ? 'modal-overlay-exit' : 'modal-overlay-enter'}`}
      style={{ backgroundColor: 'rgba(10, 10, 15, 0.85)', backdropFilter: 'blur(8px)' }}
      aria-modal="true"
      role="dialog"
    >
      <div
        ref={modalRef}
        className={`relative w-[90%] max-w-[420px] rounded-2xl border border-[rgba(245,240,232,0.08)] bg-[#141419] p-8 md:p-10 ${isClosing ? 'modal-content-exit' : 'modal-content-enter'}`}
      >
        {/* Close button */}
        <button
          onClick={handleClose}
          className="absolute right-4 top-4 text-[#8A8578] transition-colors hover:text-[#F5F0E8] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#E8D5B5] focus-visible:ring-offset-2 focus-visible:ring-offset-[#141419] rounded-lg"
          aria-label="Close modal"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Header */}
        <div className="mb-2">
          <h2
            className="text-[28px] font-medium tracking-tight text-[#F5F0E8]"
            style={{ fontFamily: "'Inter Tight', sans-serif" }}
          >
            {activeTab === 'signin' ? 'Welcome back' : 'Join Prisma'}
          </h2>
          <p className="mt-1 text-sm text-[#8A8578]">
            {activeTab === 'signin'
              ? 'Sign in to your Prisma account'
              : 'Create your Prisma account'}
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="mb-6 mt-6 flex border-b border-[rgba(245,240,232,0.08)]">
          <button
            onClick={() => setActiveTab('signin')}
            className={`pb-3 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#E8D5B5] rounded-t-lg px-2 ${
              activeTab === 'signin'
                ? 'border-b-2 border-[#F5F0E8] text-[#F5F0E8]'
                : 'text-[#8A8578] hover:text-[#F5F0E8]'
            }`}
          >
            Sign In
          </button>
          <button
            onClick={() => setActiveTab('signup')}
            className={`pb-3 ml-6 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#E8D5B5] rounded-t-lg px-2 ${
              activeTab === 'signup'
                ? 'border-b-2 border-[#F5F0E8] text-[#F5F0E8]'
                : 'text-[#8A8578] hover:text-[#F5F0E8]'
            }`}
          >
            Join
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {activeTab === 'signup' && (
            <div>
              <label className="mb-1.5 block text-[13px] text-[#8A8578]">Full name</label>
              <div className="relative">
                <User className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-[#8A8578]" />
                <input
                  type="text"
                  placeholder="Your name"
                  value={formData.fullName}
                  onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                  className="w-full rounded-lg border border-[rgba(245,240,232,0.1)] bg-[rgba(245,240,232,0.05)] py-3 pl-11 pr-4 text-[15px] text-[#F5F0E8] transition-all placeholder:text-[#8A8578]/50 focus:border-[rgba(245,240,232,0.3)] focus:shadow-[0_0_0_3px_rgba(245,240,232,0.05)] focus:outline-none"
                  required
                />
              </div>
            </div>
          )}

          <div>
            <label className="mb-1.5 block text-[13px] text-[#8A8578]">Email</label>
            <div className="relative">
              <svg className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-[#8A8578]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
              </svg>
              <input
                type="email"
                placeholder="you@example.com"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full rounded-lg border border-[rgba(245,240,232,0.1)] bg-[rgba(245,240,232,0.05)] py-3 pl-11 pr-4 text-[15px] text-[#F5F0E8] transition-all placeholder:text-[#8A8578]/50 focus:border-[rgba(245,240,232,0.3)] focus:shadow-[0_0_0_3px_rgba(245,240,232,0.05)] focus:outline-none"
                required
              />
            </div>
          </div>

          <div>
            <label className="mb-1.5 block text-[13px] text-[#8A8578]">Password</label>
            <div className="relative">
              <LockKeyhole className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-[#8A8578]" />
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="w-full rounded-lg border border-[rgba(245,240,232,0.1)] bg-[rgba(245,240,232,0.05)] py-3 pl-11 pr-12 text-[15px] text-[#F5F0E8] transition-all placeholder:text-[#8A8578]/50 focus:border-[rgba(245,240,232,0.3)] focus:shadow-[0_0_0_3px_rgba(245,240,232,0.05)] focus:outline-none"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-[#8A8578] transition-colors hover:text-[#F5F0E8]"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          {activeTab === 'signup' && (
            <div>
              <label className="mb-1.5 block text-[13px] text-[#8A8578]">Confirm password</label>
              <div className="relative">
                <LockKeyhole className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-[#8A8578]" />
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  className="w-full rounded-lg border border-[rgba(245,240,232,0.1)] bg-[rgba(245,240,232,0.05)] py-3 pl-11 pr-12 text-[15px] text-[#F5F0E8] transition-all placeholder:text-[#8A8578]/50 focus:border-[rgba(245,240,232,0.3)] focus:shadow-[0_0_0_3px_rgba(245,240,232,0.05)] focus:outline-none"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-[#8A8578] transition-colors hover:text-[#F5F0E8]"
                  aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                >
                  {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>
          )}

          {activeTab === 'signin' && (
            <div className="flex justify-end">
              <button
                type="button"
                className="text-xs text-[#8A8578] transition-colors hover:text-[#E8D5B5]"
              >
                Forgot password?
              </button>
            </div>
          )}

          {activeTab === 'signup' && (
            <label className="flex items-center gap-2.5">
              <input
                type="checkbox"
                checked={formData.agreeTerms}
                onChange={(e) => setFormData({ ...formData, agreeTerms: e.target.checked })}
                className="h-4 w-4 rounded border-[rgba(245,240,232,0.15)] bg-[rgba(245,240,232,0.05)] text-[#F5F0E8] accent-[#F5F0E8]"
                required
              />
              <span className="text-xs text-[#8A8578]">
                I agree to the{' '}
                <button type="button" className="text-[#F5F0E8] underline hover:text-[#E8D5B5]">
                  Terms of Service
                </button>{' '}
                and{' '}
                <button type="button" className="text-[#F5F0E8] underline hover:text-[#E8D5B5]">
                  Privacy Policy
                </button>
              </span>
            </label>
          )}

          <button
            type="submit"
            className="w-full rounded-full bg-[#F5F0E8] py-3.5 text-sm font-medium text-[#0A0A0F] transition-all hover:bg-white hover:scale-[1.02] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#E8D5B5] focus-visible:ring-offset-2 focus-visible:ring-offset-[#141419]"
          >
            {activeTab === 'signin' ? 'Sign In' : 'Create account'}
          </button>
        </form>

        {/* Divider */}
        <div className="my-6 flex items-center gap-4">
          <div className="h-px flex-1 bg-[rgba(245,240,232,0.08)]" />
          <span className="text-xs text-[#8A8578]">or</span>
          <div className="h-px flex-1 bg-[rgba(245,240,232,0.08)]" />
        </div>

        {/* Social buttons */}
        <div className="space-y-3">
          <button
            type="button"
            className="flex w-full items-center justify-center gap-3 rounded-lg border border-[rgba(245,240,232,0.15)] bg-transparent py-3 text-[13px] text-[#F5F0E8] transition-all hover:border-[rgba(245,240,232,0.3)] hover:bg-[rgba(245,240,232,0.03)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#E8D5B5]"
            aria-label="Continue with Google"
          >
            <Chrome className="h-4 w-4" />
            Continue with Google
          </button>
          <button
            type="button"
            className="flex w-full items-center justify-center gap-3 rounded-lg border border-[rgba(245,240,232,0.15)] bg-transparent py-3 text-[13px] text-[#F5F0E8] transition-all hover:border-[rgba(245,240,232,0.3)] hover:bg-[rgba(245,240,232,0.03)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#E8D5B5]"
            aria-label="Continue with Apple"
          >
            <Apple className="h-4 w-4" />
            Continue with Apple
          </button>
        </div>
      </div>
    </div>
  );
}

/* ─── Top Bar ─── */
function TopBar({ onLoginClick, userName }: { onLoginClick: () => void; userName: string | null }) {
  return (
    <div className="fixed left-0 right-0 top-0 z-40 flex items-center justify-between px-6 py-3">
      {/* Left side */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <div className="flex h-6 w-6 items-center justify-center rounded-md bg-gradient-to-br from-violet-500 to-indigo-600">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" className="text-white">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
          <span className="text-sm font-medium text-[#F5F0E8]">PrismaHero</span>
        </div>
        <span className="text-[#8A8578]">·</span>
        <div className="flex items-center gap-1.5">
          <Heart className="h-3.5 w-3.5 text-[#F5F0E8]" />
          <span className="text-[13px] text-[#8A8578]">Support</span>
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-1">
        <button className="rounded-lg p-2 text-[#8A8578] transition-colors hover:text-[#F5F0E8] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#E8D5B5]" aria-label="Refresh">
          <RefreshCw className="h-4 w-4" />
        </button>
        <button className="rounded-lg p-2 text-[#8A8578] transition-colors hover:text-[#F5F0E8] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#E8D5B5]" aria-label="Repeat">
          <Repeat className="h-4 w-4" />
        </button>
        <button className="rounded-lg p-2 text-[#8A8578] transition-colors hover:text-[#F5F0E8] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#E8D5B5]" aria-label="Bookmark">
          <Bookmark className="h-4 w-4" />
        </button>
        <button className="rounded-lg p-2 text-[#8A8578] transition-colors hover:text-[#F5F0E8] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#E8D5B5]" aria-label="Open external link">
          <ExternalLink className="h-4 w-4" />
        </button>
        <button className="rounded-lg px-3 py-1.5 text-[13px] text-[#F5F0E8] transition-colors hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#E8D5B5]">
          Open
        </button>
        <button className="flex items-center gap-1.5 rounded-md bg-[#2563EB] px-4 py-1.5 text-[13px] font-medium text-white transition-colors hover:bg-[#1d4ed8] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#E8D5B5]">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
            <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
          </svg>
          Copy prompt
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </button>
        <button className="rounded-lg p-2 text-[#8A8578] transition-colors hover:text-[#F5F0E8] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#E8D5B5]" aria-label="Close">
          <X className="h-4 w-4" />
        </button>
        {userName ? (
          <div className="ml-1 flex items-center gap-2 rounded-full border border-[rgba(245,240,232,0.15)] bg-[rgba(245,240,232,0.05)] px-3 py-1.5">
            <div className="flex h-5 w-5 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 text-[10px] font-medium text-white">
              {userName.charAt(0).toUpperCase()}
            </div>
            <span className="max-w-[100px] truncate text-[12px] text-[#F5F0E8]">{userName}</span>
          </div>
        ) : (
          <button
            onClick={onLoginClick}
            className="ml-1 rounded-lg border border-[rgba(245,240,232,0.15)] bg-transparent px-3 py-1.5 text-[13px] text-[#F5F0E8] transition-all hover:border-[rgba(245,240,232,0.3)] hover:bg-[rgba(245,240,232,0.05)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#E8D5B5]"
          >
            Log In
          </button>
        )}
      </div>
    </div>
  );
}

/* ─── Navigation Pill ─── */
function NavigationPill() {
  const items = ['Our story', 'Collective', 'Workshops', 'Programs', 'Inquiries'];

  return (
    <nav
      className="fixed left-1/2 top-5 z-30 -translate-x-1/2 rounded-full border border-[rgba(245,240,232,0.08)] px-10 py-3.5"
      style={{
        backgroundColor: 'rgba(10, 10, 15, 0.85)',
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)',
      }}
    >
      <ul className="flex items-center gap-10">
        {items.map((item, i) => (
          <li key={item}>
            <button
              className="animate-nav-item text-sm text-[#F5F0E8] transition-colors duration-200 hover:text-[#E8D5B5] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#E8D5B5] focus-visible:ring-offset-2 focus-visible:ring-offset-[#0A0A0F] rounded-md px-1"
              style={{ '--delay': `${600 + i * 60}ms` } as React.CSSProperties}
            >
              {item}
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
}

/* ─── Side Arrows ─── */
function SideArrows() {
  return (
    <>
      <button
        className="animate-fade-in-scale fixed left-4 top-1/2 z-10 flex h-12 w-12 items-center justify-center rounded-full border border-[rgba(245,240,232,0.1)] transition-all duration-200 hover:border-[rgba(245,240,232,0.2)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#E8D5B5]"
        style={{
          backgroundColor: 'rgba(10, 10, 15, 0.6)',
          '--delay': '800ms',
          transform: 'translateY(-50%)',
        } as React.CSSProperties}
        aria-label="Previous slide"
      >
        <ChevronLeft className="h-5 w-5 text-[#F5F0E8]" />
      </button>
      <button
        className="animate-fade-in-scale fixed right-4 top-1/2 z-10 flex h-12 w-12 items-center justify-center rounded-full border border-[rgba(245,240,232,0.1)] transition-all duration-200 hover:border-[rgba(245,240,232,0.2)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#E8D5B5]"
        style={{
          backgroundColor: 'rgba(10, 10, 15, 0.6)',
          '--delay': '800ms',
          transform: 'translateY(-50%)',
        } as React.CSSProperties}
        aria-label="Next slide"
      >
        <ChevronRight className="h-5 w-5 text-[#F5F0E8]" />
      </button>
    </>
  );
}

/* ─── Hero Content ─── */
function HeroContent() {
  return (
    <div className="fixed bottom-0 left-0 right-0 z-20 flex items-end justify-between px-10 pb-8 md:px-12">
      {/* Left — Prisma display text */}
      <div
        className="animate-fade-in-up relative"
        style={{
          '--delay': '400ms',
          '--duration': '800ms',
          '--translate-y': '40px',
        } as React.CSSProperties}
      >
        {/* The dot above 'i' */}
        <div
          className="absolute h-5 w-5 rounded-full bg-[#F5F0E8]"
          style={{
            left: 'clamp(85px, 15vw, 160px)',
            top: 'clamp(-10px, -1.5vw, -16px)',
          }}
        />
        {/* Prisma text */}
        <h1
          className="text-[clamp(60px,12vw,180px)] font-medium leading-[0.85] tracking-[-0.04em] text-[#F5F0E8]"
          style={{
            fontFamily: "'Inter Tight', sans-serif",
            textShadow: '0 2px 40px rgba(0,0,0,0.3)',
          }}
        >
          Prisma
        </h1>
        {/* Asterisk */}
        <span
          className="absolute text-[clamp(28px,4vw,48px)] font-light text-[#F5F0E8]"
          style={{
            fontFamily: "'Inter Tight', sans-serif",
            right: 'clamp(-24px, -3vw, -36px)',
            top: 'clamp(4px, 0.8vw, 10px)',
            textShadow: '0 2px 40px rgba(0,0,0,0.3)',
          }}
        >
          *
        </span>
      </div>

      {/* Right — Description + CTA */}
      <div className="flex max-w-[360px] flex-col items-start gap-5">
        <p
          className="animate-fade-in-up text-[15px] leading-relaxed text-[#F5F0E8]"
          style={{
            '--delay': '700ms',
            '--duration': '600ms',
            '--translate-y': '20px',
            textShadow: '0 1px 20px rgba(0,0,0,0.4)',
          } as React.CSSProperties}
        >
          Prisma is a worldwide network of visual artists, filmmakers and storytellers bound not by place, status or labels but by passion and hunger to unlock potential through our unique perspectives.
        </p>
        <button
          className="animate-fade-in-up group flex items-center gap-3 rounded-full bg-[#F5F0E8] px-7 py-3.5 text-sm font-medium text-[#0A0A0F] transition-all duration-200 hover:bg-white hover:scale-[1.02] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#E8D5B5]"
          style={{
            '--delay': '900ms',
            '--duration': '600ms',
            '--translate-y': '20px',
          } as React.CSSProperties}
        >
          Join the lab
          <ArrowRight className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-1" />
        </button>
      </div>
    </div>
  );
}

/* ─── Main App ─── */
function App() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [userName, setUserName] = useState<string | null>(null);
  const [toasts, setToasts] = useState<Toast[]>([]);

  const openModal = () => setIsModalOpen(true);
  const closeModal = () => setIsModalOpen(false);

  const handleLoginSuccess = (name?: string) => {
    const displayName = name || 'Member';
    setUserName(displayName);
    const newToast: Toast = {
      id: Date.now(),
      message: name ? `Welcome to Prisma, ${displayName}!` : 'Welcome back!',
      type: 'success',
    };
    setToasts((prev) => [...prev, newToast]);
  };

  const removeToast = (id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <div className="relative h-screen w-screen overflow-hidden bg-[#0A0A0F]">
      {/* Hero Background */}
      <div className="absolute inset-0 z-0 overflow-hidden">
        <img
          src="/hero-bg.jpg"
          alt="Person sitting on a floating cliff above golden clouds at sunset"
          className="hero-bg h-full w-full object-cover object-center"
          loading="eager"
        />
      </div>

      {/* Top Bar */}
      <TopBar onLoginClick={openModal} userName={userName} />

      {/* Navigation Pill */}
      <NavigationPill />

      {/* Side Arrows */}
      <SideArrows />

      {/* Hero Content */}
      <HeroContent />

      {/* Login/Signup Modal */}
      <LoginSignupModal
        isOpen={isModalOpen}
        onClose={closeModal}
        onSuccess={handleLoginSuccess}
      />

      {/* Toast Notifications */}
      {toasts.map((toast) => (
        <ToastNotification
          key={toast.id}
          toast={toast}
          onClose={() => removeToast(toast.id)}
        />
      ))}
    </div>
  );
}

export default App;
