import React, { useEffect, useRef } from 'react';
import './CyberRoninHero.css';

interface CyberRoninHeroProps {
  onEnterApp: () => void;
}

export const CyberRoninHero: React.FC<CyberRoninHeroProps> = ({ onEnterApp }) => {
  const revealImgRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // 1. Spotlight Reveal
    const handleMouseMove = (e: MouseEvent) => {
      if (!revealImgRef.current) return;
      const rect = revealImgRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const width = window.innerWidth;
      const R = width < 480 ? 120 : width < 720 ? 160 : 260;

      const maskStyle = `radial-gradient(circle ${R}px at ${x}px ${y}px, #fff 0%, #fff 40%, rgba(255,255,255,0.75) 60%, rgba(255,255,255,0.4) 75%, rgba(255,255,255,0.12) 88%, transparent 100%)`;
      revealImgRef.current.style.webkitMaskImage = maskStyle;
      revealImgRef.current.style.maskImage = maskStyle;
    };

    const handleTouchMove = (e: TouchEvent) => {
      if (e.touches && e.touches[0] && revealImgRef.current) {
        const rect = revealImgRef.current.getBoundingClientRect();
        const x = e.touches[0].clientX - rect.left;
        const y = e.touches[0].clientY - rect.top;
        const width = window.innerWidth;
        const R = width < 480 ? 120 : width < 720 ? 160 : 260;
        const maskStyle = `radial-gradient(circle ${R}px at ${x}px ${y}px, #fff 0%, #fff 40%, rgba(255,255,255,0.75) 60%, rgba(255,255,255,0.4) 75%, rgba(255,255,255,0.12) 88%, transparent 100%)`;
        revealImgRef.current.style.webkitMaskImage = maskStyle;
        revealImgRef.current.style.maskImage = maskStyle;
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('touchmove', handleTouchMove, { passive: true });

    // 2. Word Split
    let globalWordIndex = 0;
    const pullUpElements = document.querySelectorAll('.words-pull-up');

    pullUpElements.forEach((el: any) => {
      if (el.dataset.split) return;
      el.dataset.split = "true";

      const directSpans = Array.from(el.children).filter((child: any) => child.tagName.toLowerCase() === 'span');

      if (directSpans.length > 0) {
        directSpans.forEach((spanEl: any) => {
          spanEl.classList.add('pull-line');
          const words = spanEl.textContent.trim().split(/\s+/);
          spanEl.innerHTML = '';
          words.forEach((w: string) => {
            const wordSpan = document.createElement('span');
            wordSpan.className = 'pull-word';
            wordSpan.textContent = w;
            wordSpan.style.animationDelay = (globalWordIndex * 0.1).toFixed(2) + 's';
            globalWordIndex++;
            spanEl.appendChild(wordSpan);
            spanEl.appendChild(document.createTextNode(' '));
          });
        });
      } else {
        const words = el.textContent.trim().split(/\s+/);
        el.innerHTML = '';
        words.forEach((w: string) => {
          const wordSpan = document.createElement('span');
          wordSpan.className = 'pull-word';
          wordSpan.textContent = w;
          wordSpan.style.animationDelay = (globalWordIndex * 0.1).toFixed(2) + 's';
          globalWordIndex++;
          el.appendChild(wordSpan);
          el.appendChild(document.createTextNode(' '));
        });
      }
    });

    // 3. Intersection Observer Reveal
    if ('IntersectionObserver' in window) {
      const pullUpObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('words-visible');
            pullUpObserver.unobserve(entry.target);
          }
        });
      }, { threshold: 0.2 });

      pullUpElements.forEach((el) => pullUpObserver.observe(el));

      const fadeElements = document.querySelectorAll('.fade-up-reveal');
      const fadeObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const delay = entry.target.getAttribute('data-delay');
            if (delay) {
              (entry.target as HTMLElement).style.animationDelay = delay + 's';
            }
            entry.target.classList.add('is-visible');
            fadeObserver.unobserve(entry.target);
          }
        });
      }, { threshold: 0.15 });

      fadeElements.forEach((el) => fadeObserver.observe(el));
    } else {
      pullUpElements.forEach((el) => el.classList.add('words-visible'));
      document.querySelectorAll('.fade-up-reveal').forEach((el: any) => {
        const delay = el.getAttribute('data-delay');
        if (delay) el.style.animationDelay = delay + 's';
        el.classList.add('is-visible');
      });
    }

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('touchmove', handleTouchMove);
    };
  }, []);

  return (
    <div className="ronin-hero-wrapper">
      <main className="hero">
        {/* Base Layer Image */}
        <div
          className="hero-base-img hero-image-animate"
          style={{
            backgroundImage: `url('https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260831_115955_2a9adb39-5e9b-4ced-96e2-6900eabe3de9.png&w=1920&q=85')`
          }}
        ></div>

        {/* Reveal Spotlight Layer Image */}
        <div
          className="hero-reveal-img"
          ref={revealImgRef}
          style={{
            backgroundImage: `url('https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260831_123709_183f0065-efb2-4bb2-a849-13aaa5af2f3f.png&w=1920&q=85')`
          }}
        ></div>

        {/* UI Grid Overlay */}
        <div className="hero-ui">
          {/* Left Column */}
          <div className="hero-left">
            <div className="hero-copy">
              <h1 className="words-pull-up">
                <span>RONIN-X //</span>
                <span>SHADOW</span>
                <span>NIGHTFALL</span>
              </h1>
              <p className="fade-up-reveal" data-delay="0.5">
                Cultivated with high-res optics and a zero-gravity frame for those who don't just watch the future—they wield it. Shift your reality.
              </p>

              {/* Action Buttons Row */}
              <div className="cta-action-row fade-up-reveal" data-delay="0.65">
                <button onClick={onEnterApp} className="enter-trustx-main-btn">
                  ENTER TRUSTX AI COMMAND CENTER →
                </button>
              </div>

              <div className="icon-row fade-up-reveal" data-delay="0.75">
                <button className="icon-btn" aria-label="Main core" onClick={onEnterApp}>
                  <svg viewBox="0 0 16 16">
                    <path d="M8 1.4L13.8 4.7V11.3L8 14.6L2.2 11.3V4.7L8 1.4Z"></path>
                    <circle cx="8" cy="8" r="1.35" fill="currentColor"></circle>
                  </svg>
                </button>
                <button className="icon-btn" aria-label="Vision" onClick={onEnterApp}>
                  <svg viewBox="0 0 16 16">
                    <path d="M2 5.2V2h3.2" strokeLinecap="round"></path>
                    <path d="M14 5.2V2h-3.2" strokeLinecap="round"></path>
                    <path d="M2 10.8V14h3.2" strokeLinecap="round"></path>
                    <path d="M14 10.8V14h-3.2" strokeLinecap="round"></path>
                    <rect x="5.2" y="5.2" width="5.6" height="5.6"></rect>
                  </svg>
                </button>
                <button className="icon-btn" aria-label="Force" onClick={onEnterApp}>
                  <svg viewBox="0 0 16 16">
                    <path d="M9.2 1.6L4 9.1h3.5L6.8 14.4 12 6.9H8.5L9.2 1.6Z" strokeLinejoin="round"></path>
                  </svg>
                </button>
              </div>
            </div>

            {/* Product Card */}
            <article className="product-card">
              <div
                className="product-thumb"
                aria-hidden="true"
                style={{
                  backgroundImage: `url('https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260831_121937_3f02b5a0-5b86-43d9-b30e-03c5e46632e7.png&w=1920&q=85')`
                }}
              ></div>
              <div className="product-body">
                <h2 className="words-pull-up">CR-01: CYBER FRAME</h2>
                <p className="fade-up-reveal" data-delay="1.05">Precision-grade optics and a light frame for comfort and clarity.</p>
              </div>
              <button className="cart-btn fade-up-reveal" data-delay="1.15" onClick={onEnterApp}>
                Enter App →
              </button>
            </article>
          </div>

          {/* Page Counter */}
          <div className="hero-page fade-up-reveal" data-delay="0.75" onClick={onEnterApp} style={{ cursor: 'pointer' }}>
            ENTER TRUSTX 1/26 ↗
          </div>

          {/* Specs Column */}
          <div className="specs">
            <h3 className="words-pull-up">Operative Specs</h3>
            <div className="spec-row fade-up-reveal" data-delay="1.2">
              <span className="spec-label">Vision</span>
              <span className="spec-value">Dual 8K Pulse-OLED</span>
            </div>
            <div className="spec-row fade-up-reveal" data-delay="1.3">
              <span className="spec-label">Nerve</span>
              <span className="spec-value">R1 - Ronin Engines</span>
            </div>
            <div className="spec-row fade-up-reveal" data-delay="1.4">
              <span className="spec-label">Reflex</span>
              <span className="spec-value">144Hz Low-Lag Ops</span>
            </div>
            <div className="spec-row fade-up-reveal" data-delay="1.5">
              <span className="spec-label">Armor</span>
              <span className="spec-value">Lightweight Shadow Shell</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
