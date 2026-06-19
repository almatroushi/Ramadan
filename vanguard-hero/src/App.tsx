import { useState } from 'react'
import { ArrowUpRight, Award, Crown, X } from 'lucide-react'

const NAV_LINKS = ['Projects', 'Studio', 'Offerings', 'Inquire']

const STATS = [
  { value: '250+', label: 'Brands Transformed' },
  { value: '95%',  label: 'Client Retention' },
  { value: '10+',  label: 'Years in the Game' },
]

export default function App() {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <div className="relative w-full h-screen overflow-hidden bg-black">
      {/* ── Background video ── */}
      <video
        className="absolute inset-0 w-full h-full object-cover"
        src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260606_154941_df1a96e1-a06f-450c-bd02-d863414cc1a0.mp4"
        autoPlay
        muted
        loop
        playsInline
      />

      {/* Dark overlay for readability */}
      <div className="absolute inset-0 bg-black/50" />

      {/* ── Mobile menu overlay ── */}
      <div
        className={`fixed inset-0 z-50 bg-black/95 backdrop-blur-sm transition-all duration-500 md:hidden ${
          menuOpen ? 'opacity-100 visible' : 'opacity-0 invisible'
        }`}
      >
        {/* Mobile menu header */}
        <div className="flex items-center justify-between px-6 py-5">
          <span className="font-podium text-white font-bold uppercase text-2xl tracking-wider">
            VANGUARD
          </span>
          <button
            onClick={() => setMenuOpen(false)}
            className="text-white/80 hover:text-white transition-colors p-1"
            aria-label="Close menu"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Mobile menu links */}
        <div className="flex flex-col items-center justify-center h-[calc(100vh-80px)] gap-6">
          {NAV_LINKS.map((link, i) => (
            <a
              key={link}
              href="#"
              onClick={() => setMenuOpen(false)}
              className="font-podium text-white uppercase text-4xl sm:text-5xl tracking-tight transition-all duration-500"
              style={{
                transitionDelay: `${i * 80 + 100}ms`,
                opacity: menuOpen ? 1 : 0,
                transform: menuOpen ? 'translateY(0)' : 'translateY(20px)',
              }}
            >
              {link}
            </a>
          ))}

          {/* Mobile GET IN TOUCH */}
          <a
            href="#"
            onClick={() => setMenuOpen(false)}
            className="mt-6 border border-white/30 hover:border-white/60 px-8 py-4 text-white text-xs tracking-widest uppercase hover:bg-white/10 transition-all duration-300 font-inter"
            style={{
              transitionDelay: `${NAV_LINKS.length * 80 + 100}ms`,
              opacity: menuOpen ? 1 : 0,
              transform: menuOpen ? 'translateY(0)' : 'translateY(20px)',
            }}
          >
            GET IN TOUCH
          </a>
        </div>
      </div>

      {/* ── Main content layer ── */}
      <div className="relative z-10 flex flex-col h-full">

        {/* ── Navbar ── */}
        <nav className="flex items-center justify-between px-6 sm:px-10 lg:px-16 py-5 lg:py-7">
          {/* Brand */}
          <span className="font-podium text-white font-bold uppercase text-2xl sm:text-3xl tracking-wider">
            VANGUARD
          </span>

          {/* Desktop nav links */}
          <div className="hidden md:flex items-center gap-8 lg:gap-10">
            {NAV_LINKS.map((link) => (
              <a
                key={link}
                href="#"
                className="font-inter text-sm text-white/80 tracking-widest uppercase hover:text-white transition-colors duration-200"
              >
                {link}
              </a>
            ))}
          </div>

          {/* Desktop CTA */}
          <a
            href="#"
            className="hidden md:flex items-center gap-2 border border-white/30 hover:border-white/60 px-6 py-3 text-white text-xs tracking-widest uppercase hover:bg-white/10 transition-all duration-300 font-inter"
          >
            GET IN TOUCH
            <ArrowUpRight className="w-3.5 h-3.5" />
          </a>

          {/* Mobile hamburger */}
          <button
            className="md:hidden flex flex-col space-y-1.5 p-1"
            onClick={() => setMenuOpen(true)}
            aria-label="Open menu"
          >
            <div className="w-6 h-0.5 bg-white" />
            <div className="w-6 h-0.5 bg-white" />
            <div className="w-4 h-0.5 bg-white" />
          </button>
        </nav>

        {/* ── Hero content ── */}
        <div className="flex-1 flex items-center px-6 sm:px-10 lg:px-16">
          <div className="max-w-4xl">

            {/* 1. Tagline */}
            <div className="animate-fade-up flex items-center gap-2.5 mb-6 lg:mb-8">
              <Crown className="w-4 h-4 text-white/70 flex-shrink-0" />
              <span className="font-inter text-white/70 text-xs sm:text-sm tracking-[0.3em] uppercase">
                World-Class Digital Collective
              </span>
            </div>

            {/* 2. Main heading */}
            <div className="animate-fade-up-delay-1 font-podium text-white uppercase leading-[0.92] tracking-tight">
              <div style={{ fontSize: 'clamp(2.8rem, 8vw, 7rem)' }}>Design.</div>
              <div style={{ fontSize: 'clamp(2.8rem, 8vw, 7rem)' }}>Disrupt.</div>
              <div style={{ fontSize: 'clamp(2.8rem, 8vw, 7rem)' }}>Conquer.</div>
            </div>

            {/* 3. Subtext */}
            <p className="animate-fade-up-delay-2 font-inter text-white/70 text-sm sm:text-base leading-relaxed max-w-md mt-6 lg:mt-8">
              We build fierce brand identities<br />
              that don&apos;t just turn heads &mdash;{' '}
              <span className="text-white font-semibold">they lead.</span>
            </p>

            {/* 4. CTA row */}
            <div className="animate-fade-up-delay-3 flex flex-wrap items-center gap-4 sm:gap-6 mt-8 lg:mt-10">
              <a
                href="#"
                className="group inline-flex items-center gap-2 bg-black hover:bg-neutral-900 text-white px-5 sm:px-7 py-3 sm:py-4 text-[11px] sm:text-xs tracking-widest uppercase transition-colors duration-200 font-inter"
              >
                SEE OUR WORK
                <ArrowUpRight className="w-3.5 h-3.5 transition-transform duration-200 group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
              </a>

              <div className="hidden sm:flex items-center gap-3">
                <Award className="w-8 h-8 text-white/50 flex-shrink-0" />
                <div>
                  <div className="font-inter text-white/60 text-xs tracking-wider uppercase">Top-Rated</div>
                  <div className="font-inter text-white/60 text-xs tracking-wider uppercase">Brand Studio</div>
                </div>
              </div>
            </div>

            {/* 5. Stats row */}
            <div className="animate-fade-up-delay-4 flex flex-wrap gap-6 sm:gap-12 lg:gap-16 mt-8 sm:mt-10 lg:mt-14">
              {STATS.map(({ value, label }) => (
                <div key={label}>
                  <div className="font-inter text-white text-2xl sm:text-4xl lg:text-5xl font-bold tracking-tight">
                    {value}
                  </div>
                  <div className="font-inter text-white/50 text-[9px] sm:text-xs tracking-widest uppercase mt-1">
                    {label}
                  </div>
                </div>
              ))}
            </div>

          </div>
        </div>
      </div>
    </div>
  )
}
