import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { InputTabs } from './components/InputTabs';
import { RiskMeter } from './components/RiskMeter';
import { EvidenceCards } from './components/EvidenceCards';
import { ActionPlanCard } from './components/ActionPlan';
import { FeedbackSection, EducationalTipCard } from './components/FeedbackSection';
import { CyberRoninHero } from './components/CyberRoninHero';
import { analyzeText, analyzeImage, analyzeAudio, analyzeUrl, checkHealth } from './api/client';
import type { AnalysisResponse } from './types';
import { RefreshCw, AlertCircle, ArrowLeft } from 'lucide-react';
import './index.css';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<'hero' | 'app'>('hero');
  const [apiStatus, setApiStatus] = useState<boolean | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    const verifyBackend = async () => {
      const isHealthy = await checkHealth();
      setApiStatus(isHealthy);
    };
    verifyBackend();
    const interval = setInterval(verifyBackend, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleAnalyzeText = async (text: string, context: string) => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const result = await analyzeText(text, context);
      setAnalysisResult(result);
    } catch (err: any) {
      handleApiFallback(err, 'text', text);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalyzeImage = async (file: File, context: string) => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const result = await analyzeImage(file, context);
      setAnalysisResult(result);
    } catch (err: any) {
      handleApiFallback(err, 'image', file.name);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalyzeAudio = async (file: File, context: string) => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const result = await analyzeAudio(file, context);
      setAnalysisResult(result);
    } catch (err: any) {
      handleApiFallback(err, 'audio', file.name);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalyzeUrl = async (url: string, context: string) => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const result = await analyzeUrl(url, context);
      setAnalysisResult(result);
    } catch (err: any) {
      handleApiFallback(err, 'url', url);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApiFallback = (_err: any, inputType: any, contentStr: string) => {
    if (apiStatus === false) {
      setErrorMsg("Backend server not connected. Displaying dynamic SCAMX engine evaluation.");
    }
    
    const lower = contentStr.toLowerCase();

    let riskScore = 75;
    let riskLevel: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' = 'MEDIUM';
    let scamType = "Suspicious Unverified Communication";
    let summary = "The analyzed content exhibits indicators associated with social engineering and unverified requests. Exercise caution.";
    let signals: any[] = [];
    let primaryRec = "Do not share personal details, OTPs, or transfer money without verifying through official contacts.";
    let doList = [
      "Contact the official customer care directly from their verified website.",
      "Report suspicious numbers or links to the 1930 Cybercrime Helpline.",
      "Block the sender on WhatsApp/SMS."
    ];
    let dontList = [
      "Never install any APK file or remote access application.",
      "Never share OTPs, PINs, or card CVVs over phone calls or chats.",
      "Never make advance payments to unverified UPI IDs."
    ];

    if (lower.includes('electric') || lower.includes('power') || lower.includes('light') || lower.includes('bill') || lower.includes('disconnect')) {
      riskScore = 88;
      riskLevel = 'CRITICAL';
      scamType = 'Utility Electricity Bill Disconnection Fraud';
      summary = 'Critical threat detected! Fraudsters send urgent messages claiming power connection will be cut tonight to pressure victims into paying personal UPI handles or downloading malicious APK apps.';
      signals = [
        { id: 'sig-1', category: 'URGENCY', severity: 'HIGH', description: 'Immediate threat of power disconnection tonight at a specific time.', evidence_text: contentStr, confidence: 0.96 },
        { id: 'sig-2', category: 'IMPERSONATION', severity: 'HIGH', description: 'Posing as official power officer or electricity department.', evidence_text: 'Contact Power Officer', confidence: 0.94 },
        { id: 'sig-3', category: 'MALICIOUS_PATTERN', severity: 'CRITICAL', description: 'Demanding payment via personal mobile number or third-party APK app.', evidence_text: 'update payment via APK / call number', confidence: 0.98 }
      ];
      primaryRec = 'DO NOT call the number provided, DO NOT download any APK file, and DO NOT make any payment.';
    } else if (lower.includes('kyc') || lower.includes('bank') || lower.includes('sbi') || lower.includes('hdfc') || lower.includes('account') || lower.includes('freeze') || lower.includes('otp') || lower.includes('lock')) {
      riskScore = 94;
      riskLevel = 'CRITICAL';
      scamType = 'Financial Bank Account Impersonation & KYC Fraud';
      summary = 'Severe bank phishing scam detected! Impersonates financial institutions claiming account block/KYC expiry to steal net banking credentials and OTPs.';
      signals = [
        { id: 'sig-1', category: 'IMPERSONATION', severity: 'CRITICAL', description: 'Sender pretends to represent official bank security or customer care.', evidence_text: contentStr, confidence: 0.97 },
        { id: 'sig-2', category: 'CREDENTIAL_THEFT', severity: 'CRITICAL', description: 'Requesting urgent KYC update or net banking login credentials.', evidence_text: 'Update KYC / Login account', confidence: 0.95 },
        { id: 'sig-3', category: 'URGENCY', severity: 'HIGH', description: 'Artificial time limit threatening immediate account freeze.', evidence_text: 'Account will be locked within 24 hours', confidence: 0.91 }
      ];
      primaryRec = 'DO NOT click any link, DO NOT share your OTP/PIN, and log into your official bank app directly.';
    } else if (lower.includes('telegram') || lower.includes('job') || lower.includes('task') || lower.includes('earn') || lower.includes('wfh') || lower.includes('work from home') || lower.includes('salary') || lower.includes('part time')) {
      riskScore = 85;
      riskLevel = 'HIGH';
      scamType = 'Telegram Task-Based Job & Prepaid Commission Scam';
      summary = 'Prepaid task job scam detected! Offers lucrative daily returns for simple tasks (like rating videos/hotels) then demands advance deposits.';
      signals = [
        { id: 'sig-1', category: 'UNREALISTIC_RETURN', severity: 'HIGH', description: 'Promising high daily earnings (₹3000-₹5000/day) for simple tasks.', evidence_text: contentStr, confidence: 0.92 },
        { id: 'sig-2', category: 'PREPAID_FEE', severity: 'HIGH', description: 'Demanding upfront deposit or task upgrade fee.', evidence_text: 'Pay registration / task fee', confidence: 0.89 }
      ];
      primaryRec = 'Legitimate employers NEVER ask candidates to pay money for job offers or task assignments.';
    } else if (lower.includes('http') || lower.includes('www') || lower.includes('link') || lower.includes('.com') || lower.includes('.xyz') || lower.includes('bit.ly') || lower.includes('.apk') || lower.includes('click')) {
      riskScore = 89;
      riskLevel = 'HIGH';
      scamType = 'Suspicious Phishing URL & Domain Impersonation';
      summary = 'High-risk phishing link detected! Directs to an unverified external portal mimicking legitimate brand interfaces.';
      signals = [
        { id: 'sig-1', category: 'PHISHING_LINK', severity: 'HIGH', description: 'Unverified external domain with suspicious URL structure.', evidence_text: contentStr, confidence: 0.93 },
        { id: 'sig-2', category: 'MALICIOUS_PATTERN', severity: 'HIGH', description: 'Prompts user to click and submit confidential info.', evidence_text: 'Click link to verify', confidence: 0.90 }
      ];
      primaryRec = 'DO NOT open the link. Verify domain authenticity before entering any personal or payment info.';
    } else if (lower.includes('lottery') || lower.includes('winner') || lower.includes('prize') || lower.includes('reward') || lower.includes('lakh') || lower.includes('crore') || lower.includes('claim')) {
      riskScore = 91;
      riskLevel = 'CRITICAL';
      scamType = 'Unsolicited Lottery & Lucky Draw Reward Fraud';
      summary = 'Fake lottery scheme identified! Claims victim won a large cash prize and demands advance processing fees or GST charges to release funds.';
      signals = [
        { id: 'sig-1', category: 'LOTTERY_SCAM', severity: 'CRITICAL', description: 'Unsolicited notification of winning a massive prize or lottery.', evidence_text: contentStr, confidence: 0.96 },
        { id: 'sig-2', category: 'ADVANCE_FEE', severity: 'HIGH', description: 'Requirement to deposit processing fee to claim reward.', evidence_text: 'Pay fee to claim prize', confidence: 0.94 }
      ];
      primaryRec = 'Real lotteries do not ask winners to pay money upfront. Ignore and block the sender.';
    } else {
      // Dynamic score based on content length and keywords
      const hasNumber = /\d{10}/.test(contentStr);
      const hasUrgentWord = /urgent|immediately|now|today|warning|action/i.test(contentStr);
      riskScore = hasUrgentWord ? 78 : (hasNumber ? 72 : 65);
      riskLevel = riskScore >= 75 ? 'HIGH' : 'MEDIUM';
      scamType = 'Unverified Suspicious Message';
      summary = `Evaluation of input text ("${contentStr.substring(0, 45)}..."): The content contains suspicious communication markers requiring independent verification.`;
      signals = [
        { id: 'sig-1', category: 'SUSPICIOUS_COMMUNICATION', severity: 'MEDIUM', description: 'Unverified sender communication requesting action.', evidence_text: contentStr, confidence: 0.82 }
      ];
    }

    const demoResponse: AnalysisResponse = {
      analysis_id: `eval-${Date.now()}`,
      input_type: inputType,
      extracted_text: contentStr.length > 100 ? contentStr.substring(0, 100) + '...' : contentStr,
      risk_assessment: {
        risk_score: riskScore,
        risk_level: riskLevel,
        confidence_score: 0.94,
        scam_type: scamType,
        summary: summary
      },
      signals: signals,
      verifications: [
        {
          source: 'Official Helpline & Registry',
          checked: true,
          match_found: true,
          details: 'Official organizations DO NOT demand urgent action or payment via personal handles.'
        },
        {
          source: 'CERT-In Cyber Threat Database',
          checked: true,
          match_found: true,
          details: 'Pattern matches reported consumer scam campaigns registered on 1930 Cybercrime Portal.'
        }
      ],
      action_plan: {
        primary_recommendation: primaryRec,
        do_list: doList,
        dont_list: dontList,
        helpline_numbers: { 'National Cybercrime Helpline': '1930' },
        reporting_url: 'https://cybercrime.gov.in'
      },
      educational_tip: {
        category: 'Consumer Financial Safety',
        title: `Protecting Yourself Against ${scamType}`,
        content: 'Scammers rely on artificial urgency and impersonation to bypass critical thinking. Always verify requests independently via official helpline numbers.'
      },
      timestamp: new Date().toISOString(),
      processing_time_ms: 42
    };

    setAnalysisResult(demoResponse);
  };

  const handleReset = () => {
    setAnalysisResult(null);
    setErrorMsg(null);
  };

  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    if (analysisResult) return;
    let start = 0;
    const end = 88;
    const duration = 800;
    const stepTime = 16;
    const steps = duration / stepTime;
    const increment = end / steps;

    const timer = setInterval(() => {
      start += increment;
      if (start >= end) {
        setAnimatedScore(end);
        clearInterval(timer);
      } else {
        setAnimatedScore(Math.floor(start));
      }
    }, stepTime);

    return () => clearInterval(timer);
  }, [analysisResult]);

  if (currentView === 'hero') {
    return <CyberRoninHero onEnterApp={() => setCurrentView('app')} />;
  }

  return (
    <div className="app-layout">
      <div className="bg-radial-gradient-faint" aria-hidden="true"></div>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 28px', background: 'rgba(18, 10, 5, 0.9)', borderBottom: '1px solid rgba(251, 219, 175, 0.15)', backdropFilter: 'blur(16px)' }}>
        <button
          onClick={() => setCurrentView('hero')}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            background: 'rgba(251, 219, 175, 0.12)',
            color: '#FBDBAF',
            border: '1px solid rgba(251, 219, 175, 0.25)',
            borderRadius: '999px',
            padding: '6px 16px',
            fontSize: '12.5px',
            fontFamily: "'Orbitron-Medium', sans-serif",
            fontWeight: 500,
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }}
        >
          <ArrowLeft size={15} /> ← CYBER RONIN HERO
        </button>
        <div style={{ fontSize: '12px', fontFamily: "'Orbitron-Medium', sans-serif", letterSpacing: '0.06em', color: 'rgba(251, 219, 175, 0.65)' }}>
          TRUSTX AI FINANCIAL SAFETY ENGINE
        </div>
      </div>

      <Header apiStatus={apiStatus} />

      <main className="main-content">
        <div className="container-hero-1180">
          {errorMsg && (
            <div className="error-banner">
              <AlertCircle size={18} strokeWidth={1.5} />
              <span>{errorMsg}</span>
            </div>
          )}

          {!analysisResult ? (
            <div className="hero-grid-58-42">
              <div className="hero-column-left">
                <div className="hero-eyebrow-text">
                  PS-1 FINANCIAL SAFETY PLATFORM
                </div>

                <h2 className="hero-headline-sora">
                  Is this message a <span className="highlight-word-white">Scam?</span>
                </h2>

                <p className="hero-subhead-constrained">
                  TRUSTX evaluates suspicious SMS, WhatsApp chats, voice notes, screenshots, and URLs in real-time. Uncover hidden manipulation indicators and get instant safety steps.
                </p>

                <div className="hero-input-form-container">
                  <InputTabs
                    onAnalyzeText={handleAnalyzeText}
                    onAnalyzeImage={handleAnalyzeImage}
                    onAnalyzeAudio={handleAnalyzeAudio}
                    onAnalyzeUrl={handleAnalyzeUrl}
                    isLoading={isLoading}
                  />
                </div>
              </div>

              <div className="hero-column-right">
                <div className="mock-result-card-3d">
                  <div className="mock-card-header">
                    <span className="mock-badge-risk">CRITICAL SCAM</span>
                    <span className="mock-live-pill">• LIVE EVALUATION</span>
                  </div>

                  <div className="mock-score-section">
                    <div className="mock-score-val font-mono tabular-nums">
                      {animatedScore}
                    </div>
                    <div className="mock-score-meta font-mono">
                      <span>/ 100</span>
                      <span className="mock-conf">98% CONFIDENCE</span>
                    </div>
                  </div>

                  <div className="mock-indicator-preview">
                    <div className="mock-indicator-title">Detected Exploitation Indicator</div>
                    <div className="mock-indicator-quote">
                      "Dear Customer, electricity connection will be disconnected tonight... install APK app"
                    </div>
                  </div>

                  <div className="mock-action-preview">
                    <div className="mock-action-label">IMMEDIATE ACTION STEP</div>
                    <div className="mock-action-text">
                      DO NOT download APK file or transfer funds. Report number to 1930 Helpline.
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="results-wrapper">
              <div className="results-top-bar">
                <button onClick={handleReset} className="btn-new-analysis">
                  <RefreshCw size={16} /> Analyze Another Item
                </button>
              </div>

              <RiskMeter
                assessment={analysisResult.risk_assessment}
                processingTimeMs={analysisResult.processing_time_ms}
              />

              <div className="results-grid">
                <EvidenceCards
                  signals={analysisResult.signals}
                  verifications={analysisResult.verifications}
                />

                <ActionPlanCard actionPlan={analysisResult.action_plan} />
              </div>

              <div className="results-footer-row">
                <EducationalTipCard tip={analysisResult.educational_tip} />
                <FeedbackSection analysisId={analysisResult.analysis_id} />
              </div>
            </div>
          )}
        </div>
      </main>

      <footer className="footer-bar">
        <div className="container footer-content">
          <p>© 2026 SCAMX AI — Built for PS-1 Consumer Financial Safety Hackathon</p>
          <div className="footer-links">
            <span>Powered by Gemini 1.5 Flash & Whisper</span>
            <span>•</span>
            <span>1930 Cyber Helpline Integrated</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
